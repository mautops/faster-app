"""
项目配置读取工具

从 pyproject.toml 文件中读取项目配置信息
"""

import os
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional


class ProjectConfig:
    """项目配置类"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化项目配置

        Args:
            project_root: 项目根目录，如果不提供则自动查找
        """
        self.project_root = project_root
        self.config_file = self.project_root
        self._config: Optional[Dict[str, Any]] = None

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self._config is not None:
            return self._config

        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")

        try:
            with open(self.config_file, "rb") as f:
                self._config = tomllib.load(f)
            return self._config
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._load_config()

    @property
    def project_info(self) -> Dict[str, Any]:
        """获取项目基本信息"""
        config = self.config
        return config.get("project", {})

    @property
    def name(self) -> str:
        """项目名称"""
        return self.project_info.get("name", "")

    @property
    def version(self) -> str:
        """项目版本"""
        return self.project_info.get("version", "")

    @property
    def description(self) -> str:
        """项目描述"""
        return self.project_info.get("description", "")

    def to_dict(self) -> Dict[str, Any]:
        """导出为字典格式"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "scripts": self.scripts,
            "urls": self.urls,
            "build_system": self.build_system,
            "dependency_groups": self.get_dependency_groups(),
            "project_root": str(self.project_root),
            "config_file": str(self.config_file),
        }


project_config = ProjectConfig("./pyproject.toml")
