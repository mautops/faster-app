"""
CRUD 工具类 - 快速生成标准 CRUD 接口
"""

from typing import TypeVar, Generic, Type, Optional, Dict, Any, List
from tortoise import Model
from tortoise.contrib.pydantic import (
    pydantic_model_creator,
    PydanticModel,
)
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.tortoise import apaginate
from faster_app.utils.response import ApiResponse


ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=PydanticModel)


class CRUDBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]
):
    """CRUD 基类, 提供标准的增删改查操作"""

    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Optional[Type[CreateSchemaType]] = None,
        update_schema: Optional[Type[UpdateSchemaType]] = None,
        response_schema: Optional[Type[ResponseSchemaType]] = None,
    ):
        """
        初始化 CRUD 对象

        Args:
            model: Tortoise ORM 模型类
            create_schema: 创建数据的 Schema(可选, 不传则自动生成)
            update_schema: 更新数据的 Schema(可选, 不传则自动生成)
            response_schema: 响应数据的 Schema(可选, 不传则自动生成)
        """
        self.model = model

        # 没有提供 response_schema, 则自动生成
        if response_schema is None:
            self.response_schema = pydantic_model_creator(
                model, name=f"{model.__name__}Response"
            )
        else:
            self.response_schema = response_schema

        # 没有提供 create_schema, 则自动生成
        if create_schema is None:
            self.create_schema = pydantic_model_creator(
                model,
                name=f"{model.__name__}Create",
                exclude_readonly=True,  # 排除只读字段
                exclude=("id", "created_at", "updated_at"),  # 排除自动生成的字段
            )
        else:
            self.create_schema = create_schema

        # 没有提供 update_schema, 则自动生成
        if update_schema is None:
            self.update_schema = pydantic_model_creator(
                model,
                name=f"{model.__name__}Update",
                exclude_readonly=True,
                exclude=("id", "created_at", "updated_at"),
                optional=tuple(  # 所有字段都设为可选
                    field_name
                    for field_name in model._meta.fields_map.keys()
                    if field_name not in ("id", "created_at", "updated_at")
                ),
            )
        else:
            self.update_schema = update_schema

    async def before_create(self, create_data: CreateSchemaType) -> CreateSchemaType:
        """创建前的钩子函数"""
        return create_data

    async def after_create(self, instance: ModelType) -> ModelType:
        """创建后的钩子函数"""
        return instance

    async def before_update(
        self, instance: ModelType, update_data: UpdateSchemaType
    ) -> UpdateSchemaType:
        """更新前的钩子函数"""
        return update_data

    async def after_update(self, instance: ModelType) -> ModelType:
        """更新后的钩子函数"""
        return instance

    async def before_delete(self, instance: ModelType) -> bool:
        """删除前的钩子函数, 返回 False 可以阻止删除"""
        return True

    async def after_delete(self, instance: ModelType) -> None:
        """删除后的钩子函数"""
        pass

    async def get(
        self, record_id: Any, prefetch: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        根据 ID 获取单条记录

        Args:
            record_id: 记录 ID
            prefetch: 需要预加载的关联字段列表
        """
        query = self.model.get_or_none(id=record_id)
        if prefetch:
            query = query.prefetch_related(*prefetch)
        return await query

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        prefetch: Optional[List[str]] = None,
    ) -> List[ModelType]:
        """
        获取多条记录

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            filters: 过滤条件(Tortoise ORM 格式)
            order_by: 排序字段列表
            prefetch: 需要预加载的关联字段列表
        """
        query = self.model.all()

        if filters:
            query = query.filter(**filters)

        if order_by:
            query = query.order_by(*order_by)

        if prefetch:
            query = query.prefetch_related(*prefetch)

        return await query.offset(skip).limit(limit)

    async def get_by_filters(self, **filters) -> Optional[ModelType]:
        """根据条件获取单条记录"""
        return await self.model.filter(**filters).first()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数"""
        query = self.model.all()
        if filters:
            query = query.filter(**filters)
        return await query.count()

    async def exists(self, **filters) -> bool:
        """检查记录是否存在"""
        return await self.model.filter(**filters).exists()

    async def create(self, create_data: CreateSchemaType) -> ModelType:
        """
        创建记录

        支持 before_create 和 after_create 钩子函数
        """
        # 执行创建前钩子
        create_data = await self.before_create(create_data)

        # 创建记录
        data_dict = create_data.model_dump(exclude_unset=True)
        instance = await self.model.create(**data_dict)

        # 执行创建后钩子
        instance = await self.after_create(instance)

        return instance

    async def create_many(self, items_data: List[CreateSchemaType]) -> List[ModelType]:
        """批量创建记录"""
        instances = []
        for create_data in items_data:
            create_data = await self.before_create(create_data)
            data_dict = create_data.model_dump(exclude_unset=True)
            instance = self.model(**data_dict)
            instances.append(instance)

        await self.model.bulk_create(instances)

        for instance in instances:
            await self.after_create(instance)

        return instances

    async def update(
        self, record_id: Any, update_data: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        更新记录

        支持 before_update 和 after_update 钩子函数
        """
        instance = await self.get(record_id)
        if not instance:
            return None

        # 执行更新前钩子
        update_data = await self.before_update(instance, update_data)

        # 更新记录
        data_dict = update_data.model_dump(exclude_unset=True)
        await instance.update_from_dict(data_dict)
        await instance.save()

        # 执行更新后钩子
        instance = await self.after_update(instance)

        return instance

    async def delete(self, record_id: Any) -> bool:
        """
        删除记录

        支持 before_delete 和 after_delete 钩子函数
        """
        instance = await self.get(record_id)
        if not instance:
            return False

        # 执行删除前钩子
        can_delete = await self.before_delete(instance)
        if not can_delete:
            return False

        # 删除记录
        await instance.delete()

        # 执行删除后钩子
        await self.after_delete(instance)

        return True

    async def delete_many(self, record_ids: List[Any]) -> int:
        """批量删除记录, 返回删除的数量"""
        deleted_count = 0
        for record_id in record_ids:
            if await self.delete(record_id):
                deleted_count += 1
        return deleted_count


class CRUDRouter(Generic[ModelType]):
    """
    CRUD 路由生成器 - 自动生成标准的 CRUD 路由

    Example:
        # 快速模式 - 使用自动生成的 schemas
        router = CRUDRouter(
            model=DemoModel,
            prefix="/demos",
            tags=["Demo"]
        ).get_router()

        # 自定义模式 - 使用自定义 schemas
        router = CRUDRouter(
            model=DemoModel,
            create_schema=DemoCreate,
            update_schema=DemoUpdate,
            response_schema=DemoResponse,
            prefix="/demos",
            tags=["Demo"]
        ).get_router()

        # 扩展模式 - 添加自定义路由
        crud_router = CRUDRouter(model=DemoModel, prefix="/demos", tags=["Demo"])
        router = crud_router.get_router()

        @router.get("/custom")
        async def custom_endpoint():
            return {"message": "自定义端点"}
    """

    def __init__(
        self,
        model: Type[ModelType],
        prefix: str = "",
        tags: Optional[List[str]] = None,
        create_schema: Optional[Type[BaseModel]] = None,
        update_schema: Optional[Type[BaseModel]] = None,
        response_schema: Optional[Type[PydanticModel]] = None,
        operations: str = "CRUDL",
    ):
        """
        初始化 CRUD 路由生成器

        Args:
            model: Tortoise ORM 模型类
            prefix: 路由前缀
            tags: OpenAPI 标签
            create_schema: 创建数据的 Schema
            update_schema: 更新数据的 Schema
            response_schema: 响应数据的 Schema
            operations: 支持的操作, 使用字符串表示:
                - C: Create (创建)
                - R: Read (读取单个)
                - U: Update (更新)
                - D: Delete (删除)
                - L: List (列表查询)
                默认 "CRUDL" 表示全部支持
                示例:
                    - "CRUDL" - 全部功能
                    - "RL" - 只读模式(只支持查询)
                    - "CL" - 只支持创建和列表
                    - "CRUD" - 不支持列表查询
        """
        self.model = model
        self.router = APIRouter(prefix=prefix, tags=tags or [model.__name__])
        self.operations = operations.upper()  # 统一转为大写

        # 初始化 CRUD 操作类
        self.crud = CRUDBase(
            model=model,
            create_schema=create_schema,
            update_schema=update_schema,
            response_schema=response_schema,
        )

        # 根据 operations 字符串注册路由
        if "L" in self.operations:
            self._register_list_route()
        if "C" in self.operations:
            self._register_create_route()
        if "R" in self.operations:
            self._register_read_route()
        if "U" in self.operations:
            self._register_update_route()
        if "D" in self.operations:
            self._register_delete_route()

    def _register_list_route(self):
        """注册列表查询路由(支持分页)"""

        @self.router.get("/", response_model=Page[self.crud.response_schema])
        async def list_records(pagination: Params = Depends()):
            """查询列表(分页)"""
            return await apaginate(query=self.model.all(), params=pagination)

    def _register_create_route(self):
        """注册创建路由"""

        @self.router.post("/", response_model=self.crud.response_schema)
        async def create_record(create_data: self.crud.create_schema):
            """创建新记录"""
            record = await self.crud.create(create_data)
            return await self.crud.response_schema.from_tortoise_orm(record)

    def _register_read_route(self):
        """注册读取单个路由"""

        @self.router.get("/{record_id}", response_model=self.crud.response_schema)
        async def read_record(record_id: str):
            """根据 ID 查询单条记录"""
            record = await self.crud.get(record_id)
            if not record:
                raise HTTPException(status_code=404, detail="记录不存在")
            return await self.crud.response_schema.from_tortoise_orm(record)

    def _register_update_route(self):
        """注册更新路由"""

        @self.router.put("/{record_id}", response_model=self.crud.response_schema)
        async def update_record(record_id: str, update_data: self.crud.update_schema):
            """更新记录"""
            record = await self.crud.update(record_id, update_data)
            if not record:
                raise HTTPException(status_code=404, detail="记录不存在")
            return await self.crud.response_schema.from_tortoise_orm(record)

    def _register_delete_route(self):
        """注册删除路由"""

        @self.router.delete("/{record_id}")
        async def delete_record(record_id: str):
            """删除记录"""
            success = await self.crud.delete(record_id)
            if not success:
                raise HTTPException(status_code=404, detail="记录不存在")
            return ApiResponse.success(message="删除成功")

    def get_router(self) -> APIRouter:
        """获取生成的路由"""
        return self.router

    def add_custom_route(self, path: str, **kwargs):
        """
        装饰器:添加自定义路由

        Example:
            crud_router = CRUDRouter(model=User, prefix="/users")

            @crud_router.add_custom_route("/stats", methods=["GET"])
            async def user_stats():
                return {"total": await User.all().count()}
        """

        def decorator(func):
            self.router.add_api_route(path, func, **kwargs)
            return func

        return decorator
