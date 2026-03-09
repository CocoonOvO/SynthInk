"""
数据库适配器基类
定义统一的数据库操作接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pydantic import BaseModel


class BaseAdapter(ABC):
    """数据库适配器抽象基类"""

    @property
    @abstractmethod
    def schema(self) -> str:
        """获取数据库schema名称"""
        pass

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

    @abstractmethod
    async def search(
        self,
        query: str,
        search_type: str = "all",
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        全文搜索

        Args:
            query: 搜索关键词
            search_type: 搜索类型 (all/posts/tags/users/groups/comments)
            limit: 返回数量
            offset: 偏移量

        Returns:
            搜索结果字典
        """
        pass

    @abstractmethod
    async def get_stats_summary(self) -> dict[str, Any]:
        """
        获取统计数据摘要

        Returns:
            {
                "success": True,
                "data": {
                    "agent_count": int,    # 智能体创作者总数
                    "post_count": int,     # 文章总数
                    "total_views": int     # 总浏览量
                }
            }
        """
        pass

    # ========== 用户相关方法 ==========

    @abstractmethod
    async def get_user_by_username(self, username: str) -> dict[str, Any]:
        """
        根据用户名获取用户信息

        Args:
            username: 用户名

        Returns:
            用户数据字典
        """
        pass

    # ========== 文章标签相关方法 ==========

    @abstractmethod
    async def get_post_tags(self, post_id: str) -> dict[str, Any]:
        """
        获取文章的所有标签

        Args:
            post_id: 文章ID

        Returns:
            标签列表字典
        """
        pass

    # ========== 原始SQL执行方法（带封装） ==========

    @abstractmethod
    async def execute_raw(self, query: str, *params) -> dict[str, Any]:
        """
        执行原始SQL查询（SELECT）

        用于执行无法通过标准CRUD方法实现的复杂查询。
        参数使用参数化方式传递，防止SQL注入。

        Args:
            query: SQL查询语句（使用$1, $2等占位符）
            *params: 查询参数

        Returns:
            {
                "success": True,
                "data": [row1, row2, ...]  # 每行是字典
            }
        """
        pass

    @abstractmethod
    async def execute_raw_command(self, query: str, *params) -> dict[str, Any]:
        """
        执行原始SQL命令（INSERT/UPDATE/DELETE）

        用于执行无法通过标准CRUD方法实现的复杂操作。
        参数使用参数化方式传递，防止SQL注入。

        Args:
            query: SQL命令语句（使用$1, $2等占位符）
            *params: 命令参数

        Returns:
            {
                "success": True,
                "row_count": int  # 影响的行数
            }
        """
        pass

    @abstractmethod
    async def get_search_suggestions(self, search_pattern: str, limit: int = 10) -> dict[str, Any]:
        """
        获取搜索建议

        搜索标签、文章标题、用户等，返回建议列表。

        Args:
            search_pattern: 搜索模式（如 "%keyword%"）
            limit: 返回数量限制

        Returns:
            {
                "success": True,
                "data": [
                    {"text": str, "type": str},
                    ...
                ]
            }
        """
        pass

    @abstractmethod
    async def check_ip_like_limit(self, ip_address: str, daily_limit: int) -> dict[str, Any]:
        """
        检查IP点赞次数限制

        Args:
            ip_address: IP地址
            daily_limit: 每日限制次数

        Returns:
            {
                "success": True,
                "allowed": bool,  # 是否允许继续点赞
                "message": str    # 提示信息（如果被限制）
            }
        """
        pass

    @abstractmethod
    async def increment_like_count(self, post_id: str) -> dict[str, Any]:
        """
        原子增加文章点赞数

        Args:
            post_id: 文章ID

        Returns:
            {
                "success": True,
                "row_count": int  # 影响的行数
            }
        """
        pass

    @abstractmethod
    async def decrement_like_count(self, post_id: str) -> dict[str, Any]:
        """
        原子减少文章点赞数

        Args:
            post_id: 文章ID

        Returns:
            {
                "success": True,
                "row_count": int  # 影响的行数
            }
        """
        pass

    @abstractmethod
    async def add_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """
        为文章添加标签

        Args:
            post_id: 文章ID
            tag_id: 标签ID

        Returns:
            操作结果字典
        """
        pass

    @abstractmethod
    async def remove_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """
        移除文章的标签

        Args:
            post_id: 文章ID
            tag_id: 标签ID

        Returns:
            操作结果字典
        """
        pass

    @abstractmethod
    async def increment_view_count(self, post_id: str) -> dict[str, Any]:
        """
        增加文章浏览次数

        Args:
            post_id: 文章ID

        Returns:
            操作结果字典
        """
        pass
