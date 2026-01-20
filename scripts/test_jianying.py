"""
测试剪映功能
"""
import asyncio

from loguru import logger

from backend.integrations.py_jianying.draft_manager import draft_manager


async def test_list_jianying_drafts():
    """测试列出剪映草稿箱中的草稿"""
    logger.info("=" * 50)
    logger.info("测试：列出剪映草稿箱中的草稿")
    logger.info("=" * 50)
    
    drafts = draft_manager.list_drafts()
    
    if not drafts:
        logger.warning("剪映草稿箱中没有草稿")
    else:
        logger.info(f"找到 {len(drafts)} 个草稿：")
        for draft in drafts:
            logger.info(f"  - {draft['draft_name']} (ID: {draft['draft_id']})")
            logger.info(f"    路径: {draft['draft_path']}")
            logger.info(f"    时长: {draft['duration']} 秒")
            logger.info(f"    加密: {draft['is_encrypted']}")
            logger.info("")


async def test_get_draft_info():
    """测试获取指定草稿的信息"""
    logger.info("=" * 50)
    logger.info("测试：获取指定草稿的信息")
    logger.info("=" * 50)
    
    # 先列出所有草稿
    drafts = draft_manager.list_drafts()
    
    if not drafts:
        logger.warning("剪映草稿箱中没有草稿，跳过测试")
        return
    
    # 获取第一个草稿的详细信息
    first_draft_id = drafts[0]['draft_id']
    logger.info(f"获取草稿 {first_draft_id} 的信息...")
    
    draft_info = draft_manager.get_draft_info(first_draft_id)
    
    if draft_info:
        logger.info(f"草稿信息：")
        logger.info(f"  名称: {draft_info['draft_name']}")
        logger.info(f"  ID: {draft_info['draft_id']}")
        logger.info(f"  路径: {draft_info['draft_path']}")
        logger.info(f"  时长: {draft_info['duration']} 秒")
        logger.info(f"  加密: {draft_info['is_encrypted']}")
    else:
        logger.error(f"获取草稿信息失败")


async def test_create_draft_folder():
    """测试创建草稿文件夹"""
    logger.info("=" * 50)
    logger.info("测试：创建草稿文件夹")
    logger.info("=" * 50)
    
    draft_name = "test_draft"
    draft_path = draft_manager.create_draft_folder(draft_name)
    
    logger.info(f"创建草稿文件夹成功: {draft_path}")
    
    # 清理测试文件夹
    draft_manager.delete_draft_folder(draft_path)
    logger.info(f"清理测试文件夹成功")


async def main():
    """主测试函数"""
    logger.info("开始测试剪映功能...")
    logger.info("")
    
    # 测试 1: 列出剪映草稿箱中的草稿
    await test_list_jianying_drafts()
    
    # 测试 2: 获取指定草稿的信息
    await test_get_draft_info()
    
    # 测试 3: 创建草稿文件夹
    await test_create_draft_folder()
    
    logger.info("")
    logger.info("所有测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
