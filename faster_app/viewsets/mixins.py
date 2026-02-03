"""
ViewSet Mixin 类

提供可组合的 CRUD 操作 Mixin,使用组合模式实现灵活的功能组合。
"""

from typing import Any

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import apaginate
from pydantic import BaseModel
from tortoise import Model

from faster_app.exceptions import NotFoundError
from faster_app.utils.response import ApiResponse

# 模块级别的默认分页实例,用于避免在函数参数默认值中调用函数
_DEFAULT_PAGINATION = Params()


class ListModelMixin:
    """
    列表查询 Mixin

    提供 list() 方法用于查询列表(支持分页)
    """

    async def list(
        self,
        request: Request,
        pagination: Params = _DEFAULT_PAGINATION,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        查询列表(支持分页和过滤)

        Args:
            request: FastAPI 请求对象
            pagination: 分页参数
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            ApiResponse 格式的分页结果
        """
        # 检查限流
        await self.check_throttles(request)
        # 执行认证
        await self.perform_authentication(request)
        # 检查权限
        await self.check_permissions(request, "list")

        # 获取查询集
        queryset = self.get_queryset()
        # 应用过滤
        queryset = await self.filter_queryset(queryset, request)

        # 获取分页结果
        page = await apaginate(query=queryset, params=pagination)

        # 获取 Schema 类
        schema = self.get_schema("list")

        # 序列化每个对象并转换为字典(使用 mode='json' 以正确处理 UUID 等类型)
        serialized_items = [
            (await schema.from_orm_model(item)).model_dump(mode="json") for item in page.items
        ]

        # 创建分页数据
        page_data = {
            "items": serialized_items,
            "total": page.total,
            "page": page.page,
            "size": page.size,
            "pages": page.pages,
        }

        return ApiResponse.success(  # type: ignore[return-value]
            data=page_data,
            message="查询成功",
        )


class CreateModelMixin:
    """
    创建 Mixin

    提供 create() 方法用于创建新记录
    """

    async def create(
        self,
        request: Request,
        create_data: BaseModel,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        创建新记录

        Args:
            request: FastAPI 请求对象
            create_data: 创建数据的 Schema 实例
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            ApiResponse 格式的创建结果
        """
        # 检查限流
        await self.check_throttles(request)
        # 执行认证
        await self.perform_authentication(request)
        # 检查权限
        await self.check_permissions(request, "create")

        # 执行创建前钩子
        create_data = await self.perform_create_hook(create_data, request)

        # 创建记录
        instance = await self.perform_create(create_data)

        # 执行创建后钩子
        instance = await self.perform_create_after_hook(instance, request)

        # 序列化数据
        schema = self.get_schema("retrieve")
        serialized_data = await schema.from_orm_model(instance)

        return ApiResponse.success(  # type: ignore[return-value]
            data=serialized_data.model_dump(mode="json"),
            message="创建成功",
        )

    async def perform_create(self, create_data: BaseModel) -> Model:
        """
        执行创建操作(可被子类重写)

        Args:
            create_data: 创建数据的 Schema 实例

        Returns:
            创建的模型实例
        """
        data_dict = create_data.model_dump(exclude_unset=True)
        return await self.model.create(**data_dict)

    async def perform_create_hook(self, create_data: BaseModel, request: Request) -> BaseModel:
        """
        创建前钩子(可被子类重写)

        Args:
            create_data: 创建数据的 Schema 实例
            request: FastAPI 请求对象

        Returns:
            处理后的创建数据
        """
        return create_data

    async def perform_create_after_hook(self, instance: Model, request: Request) -> Model:
        """
        创建后钩子(可被子类重写)

        Args:
            instance: 创建的模型实例
            request: FastAPI 请求对象

        Returns:
            处理后的模型实例
        """
        return instance


class RetrieveModelMixin:
    """
    单个查询 Mixin

    提供 retrieve() 方法用于查询单个记录
    """

    async def retrieve(
        self,
        request: Request,
        pk: Any,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        查询单个记录

        Args:
            request: FastAPI 请求对象
            pk: 记录主键
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            ApiResponse 格式的查询结果

        Raises:
            NotFoundError: 记录不存在
        """
        # 检查限流
        await self.check_throttles(request)
        # 执行认证
        await self.perform_authentication(request)

        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})

        # 检查对象级权限
        await self.check_object_permissions(request, instance, "retrieve")

        schema = self.get_schema("retrieve")
        serialized_data = await schema.from_orm_model(instance)

        return ApiResponse.success(
            data=serialized_data.model_dump(mode="json"),
            message="查询成功",
        )


class UpdateModelMixin:
    """
    更新 Mixin

    提供 update() 和 partial_update() 方法用于更新记录
    """

    async def update(
        self,
        request: Request,
        pk: Any,
        update_data: BaseModel,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        完整更新记录

        Args:
            request: FastAPI 请求对象
            pk: 记录主键
            update_data: 更新数据的 Schema 实例
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            ApiResponse 格式的更新结果

        Raises:
            NotFoundError: 记录不存在
        """
        # 检查限流
        await self.check_throttles(request)
        # 执行认证
        await self.perform_authentication(request)

        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})

        # 检查对象级权限
        await self.check_object_permissions(request, instance, "update")

        # 执行更新前钩子
        update_data = await self.perform_update_hook(instance, update_data, request)

        # 更新记录
        instance = await self.perform_update(instance, update_data)

        # 执行更新后钩子
        instance = await self.perform_update_after_hook(instance, request)

        # 序列化数据
        schema = self.get_schema("retrieve")
        serialized_data = await schema.from_orm_model(instance)

        return ApiResponse.success(  # type: ignore[return-value]
            data=serialized_data.model_dump(mode="json"),
            message="更新成功",
        )

    async def partial_update(
        self,
        request: Request,
        pk: Any,
        update_data: BaseModel,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        部分更新记录(PATCH)

        Args:
            request: FastAPI 请求对象
            pk: 记录主键
            update_data: 更新数据的 Schema 实例(只包含要更新的字段)
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            ApiResponse 格式的更新结果

        Raises:
            NotFoundError: 记录不存在
        """
        # partial_update 和 update 使用相同的逻辑
        # 区别在于 update_data 只包含要更新的字段
        return await self.update(request, pk, update_data, *args, **kwargs)

    async def perform_update(self, instance: Model, update_data: BaseModel) -> Model:
        """
        执行更新操作(可被子类重写)

        Args:
            instance: 要更新的模型实例
            update_data: 更新数据的 Schema 实例

        Returns:
            更新后的模型实例
        """
        data_dict = update_data.model_dump(exclude_unset=True)
        await instance.update_from_dict(data_dict)
        await instance.save()
        return instance

    async def perform_update_hook(
        self, instance: Model, update_data: BaseModel, request: Request
    ) -> BaseModel:
        """
        更新前钩子(可被子类重写)

        Args:
            instance: 要更新的模型实例
            update_data: 更新数据的 Schema 实例
            request: FastAPI 请求对象

        Returns:
            处理后的更新数据
        """
        return update_data

    async def perform_update_after_hook(self, instance: Model, request: Request) -> Model:
        """
        更新后钩子(可被子类重写)

        Args:
            instance: 更新后的模型实例
            request: FastAPI 请求对象

        Returns:
            处理后的模型实例
        """
        return instance


class DestroyModelMixin:
    """
    删除 Mixin

    提供 destroy() 方法用于删除记录
    """

    async def destroy(
        self,
        request: Request,
        pk: Any,
        *args: Any,
        **kwargs: Any,
    ) -> ApiResponse:
        """
        删除记录

        Args:
            request: FastAPI 请求对象
            pk: 记录主键
            *args: 额外位置参数
            **kwargs: 额外关键字参数

        Returns:
            删除成功的响应

        Raises:
            NotFoundError: 记录不存在
        """
        # 检查限流
        await self.check_throttles(request)
        # 执行认证
        await self.perform_authentication(request)

        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})

        # 检查对象级权限
        await self.check_object_permissions(request, instance, "destroy")

        # 执行删除前钩子
        can_delete = await self.perform_destroy_hook(instance, request)
        if not can_delete:
            raise NotFoundError(message="无法删除该记录", data={"pk": pk})

        # 删除记录
        await self.perform_destroy(instance)

        # 执行删除后钩子
        await self.perform_destroy_after_hook(instance, request)

        return ApiResponse.success(message="删除成功")  # type: ignore[return-value]

    async def perform_destroy(self, instance: Model) -> None:
        """
        执行删除操作(可被子类重写)

        Args:
            instance: 要删除的模型实例
        """
        await instance.delete()

    async def perform_destroy_hook(self, instance: Model, request: Request) -> bool:
        """
        删除前钩子(可被子类重写)

        Args:
            instance: 要删除的模型实例
            request: FastAPI 请求对象

        Returns:
            True 允许删除,False 阻止删除
        """
        return True

    async def perform_destroy_after_hook(self, instance: Model, request: Request) -> None:
        """
        删除后钩子(可被子类重写)

        Args:
            instance: 已删除的模型实例(已从数据库删除,但对象仍存在)
            request: FastAPI 请求对象
        """
        pass
