"""
数据库适配器基类
定义统一的数据库操作接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pydantic import BaseModel


class BaseAdapter(ABC):
    """数据库适配器抽象基类"""
    
    @abstractmethod
    async def connect(self) -> None:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    async def create_table(self, name: str) -> dict[str, Any]:
        """创建数据表/集合"""
        pass
    
    @abstractmethod
    async def drop_table(self, name: str) -> dict[str, Any]:
        """删除数据表/集合"""
        pass
    
    @abstractmethod
    async def insert(self, table: str, data: Union[BaseModel, dict]) -> dict[str, Any]:
        """插入数据"""
        pass
    
    @abstractmethod
    async def get(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """根据ID获取数据"""
        pass
    
    @abstractmethod
    async def update(self, table: str, id: Union[str, int], data: dict) -> dict[str, Any]:
        """更新数据"""
        pass
    
    @abstractmethod
    async def delete(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """删除数据"""
        pass
    
    @abstractmethod
    async def find(
        self, 
        table: str, 
        filters: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> dict[str, Any]:
        """条件查询"""
        pass
    
    @abstractmethod
    async def count(self, table: str, filters: Optional[dict] = None) -> dict[str, Any]:
        """统计数量"""
        pass
    
    @abstractmethod
    async def init_schema(self) -> None:
        """初始化数据库结构"""
        pass
