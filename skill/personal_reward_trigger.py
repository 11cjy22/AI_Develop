"""个人中心激励广告触发策略"""
import asyncio
import os
from typing import Dict, Any

from PIL import Image
import traceback

from automation_engine.components.helpers.strategy_base import StrategyBase
from automation_engine.context.execution import ExecutionContext
from automation_engine.definitions import LogLevel
from automation_engine.drivers.base import LocatorStrategy, Locator

class RewardTrigger(StrategyBase):
    """
    激励广告统一进入策略

    支持的入口类型:
    1. homepage - 首页场景（首页挂件/拍脸图）
    2. detail - 详情页场景（详情页挂件/底图banner/解锁面板）
    3. personal - 个人中心场景（个人中心挂件/常驻bar）

    特点:
    - 只负责进入对应页面，不关闭免费看弹窗
    - Yaml配置进行UI校验
    - 通过 reward_config.entry_page 参数区分场景
    """
    def __init__(self, component=None):
        """初始化策略"""
        super().__init__(component)
        self._helper = None  # 延迟初始化 helper

    @property
    def helper(self):
        """获取 VideoTriggerHelper 实例（延迟初始化）"""
        if self._helper is None:
            self._helper = self.get_video_trigger_helper()
        return self._helper
    # 场景配置映射
    SCENE_CONFIG = {
        "homepage_widget": {
            "name": "首页挂件",
            "verify_text": "首页",  # 验证文本
        },
        "homepage_face": {
            "name": "首页拍脸图",
            "verify_text": "首页",  # 验证文本
        },
        "detail_widget": {
            "name": "详情页挂件",
            "verify_text": None,  # 详情页通过其他方式验证
        },
        "detail_banner": {
            "name": "详情页banner",
            "verify_text": None,  # 详情页通过其他方式验证
        },
        "detail_unlock": {
            "name": "详情页解锁页面",
            "verify_text": None,  # 详情页通过其他方式验证
        },
        "personal": {
            "name": "个人中心",
            "verify_text": "个人中心",
        }
    }


    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> bool:
        """
        根据配置进入对应的激励广告场景
        """
        ops = context.get_operations()

        # 获取基础参数
        app_package = inputs.get("app_package")
        platform = inputs.get("platform", "android").lower()
        reward_config = context.get_variable("reward_config") or {}
        entry_page = reward_config.get("entry_page", "personal")  # 默认个人中心

        # 验证场景配置
        if entry_page not in self.SCENE_CONFIG:
            self.add_log(LogLevel.ERROR, f"不支持的入口页面类型: {entry_page}, 支持的类型: {list(self.SCENE_CONFIG.keys())}")
            return False

        scene_config = self.SCENE_CONFIG[entry_page]
        self.add_log(LogLevel.INFO, f"执行激励广告进入策略 - 场景: {scene_config['name']} - 平台: {platform}")

        try:
            # 1. 重启应用
            restart = await ops.app_restart(app_package)
            if not restart:
                self.add_log(LogLevel.ERROR, "重启应用失败")
                return False
            await asyncio.sleep(10)

            # 2. 调用 Helper 关闭可能出现的开屏/登录弹窗
            await self.helper.close_login_popup(ops)

            # 3. 根据场景类型执行不同的进入逻辑
            if entry_page == "homepage_face":
                success = await self._enter_homepage(ops, platform, entry_page)
            elif entry_page == "homepage_widget":
                success = await self._enter_homepage(ops, platform, entry_page)
            elif entry_page == "detail_widget" or entry_page == "detail_banner" or entry_page == "detail_unlock":
                success = await self._enter_detail_page(ops, platform, context, inputs, entry_page)
            elif entry_page == "personal":
                success = await self._enter_personal_center(ops, context, platform)
            else:
                self.add_log(LogLevel.ERROR, f"未实现的场景类型: {entry_page}")
                return False

            if not success:
                self.add_log(LogLevel.ERROR, f"进入{scene_config['name']}失败")
                return False

            self.add_log(LogLevel.INFO, f"✅ 成功进入{scene_config['name']}")
            return True

        except Exception as e:
            import traceback
            self.add_log(LogLevel.ERROR, f"进入激励广告场景异常: {str(e)}\n{traceback.format_exc()}")
            return False

    async def _enter_homepage(self, ops, platform: str, entry_page) -> bool:
        """首页拍脸图"""
        self.add_log(LogLevel.INFO, "开始进入首页场景")
        try:
            # 调用 Helper 的能力进入首页
            await self.helper.click_first_page(ops)
            await asyncio.sleep(3)

            if entry_page == "homepage_widget":
                await self.helper.close_bottom_free_view_popup(ops)
            # 验证是否在首页
            verify_text = "首页"
            home_element = await ops.find_by_text(
                text=verify_text,
                strategy_priority=[LocatorStrategy.TEXT.value, LocatorStrategy.OCR_TEXT.value],
                timeout=5
            )
            if home_element:
                self.add_log(LogLevel.INFO, f"✓ 已在首页，找到验证元素: {verify_text}")
                return True
            else:
                self.add_log(LogLevel.WARNING, f"未找到首页验证元素: {verify_text}")
                return False
        except Exception as e:
            self.add_log(LogLevel.ERROR, f"进入首页异常: {str(e)}")
            return False


    async def _enter_detail_page(self, ops, platform: str, context: ExecutionContext, inputs: Dict[str, Any], entry_page) -> bool:
        """进入详情页场景"""
        self.add_log(LogLevel.INFO, "开始进入详情页场景")

        video_info = inputs.get('video', {})
        vid = video_info.get('vid', None)
        pid = video_info.get('pid', None)
        ad_show_time = video_info.get('ad_show_time', 240000)
        if vid is not None:
            video_type = "vid"
            video_id = vid
        elif pid is not None:
            video_type = "pid"
            video_id = pid
        else:
            self.add_log(LogLevel.ERROR, "yaml中视频信息中缺少vid或pid")
            return False
        try:
            if platform == "android":
                self.add_log(LogLevel.INFO, "平台是android，通过 intent 拉起详情页")
                await self.helper.start_app_by_intent(ops, video_id, video_type)
                await asyncio.sleep(5)
                if entry_page == "detail_widget" or entry_page == "detail_unlock":
                    # 详情页挂件、解锁面板关闭权益弹窗
                    await asyncio.sleep(10)
                    await self.helper.handle_give_up_rights_popup(ops)
            elif platform == "ios":
                pass        #ios的策略暂未实现
            return True

        except Exception as e:
            self.add_log(LogLevel.ERROR, f"进入详情页异常: {str(e)}")
            return False

    async def _enter_personal_center(self, ops, context, platform: str) -> bool:
        """进入个人中心场景"""
        self.add_log(LogLevel.INFO, "开始进入个人中心场景")
        try:
            await self.helper.enter_person_center(ops)
            await asyncio.sleep(3)
            await self.helper.close_login_popup(ops)
            await asyncio.sleep(3)
            self.add_log(LogLevel.INFO, "✓ 成功进入个人中心")
            screenshot_path = os.path.abspath(f"{context.out_dir}/ui_diff_compare_pic_path.png")
            success = await ops.save_screenshot(screenshot_path)
            if success:
                try:
                    # ================= 新增：裁剪上半部分逻辑 =================
                    # 打开刚才保存的截图
                    img = Image.open(screenshot_path)
                    width, height = img.size
                    # 定义裁剪区域 (left, upper, right, lower)
                    # 上半部分：左上角(0,0)，右下角(width, height/2)
                    crop_box = (0, 0, width, int(height / 2))
                    # 执行裁剪
                    cropped_img = img.crop(crop_box)
                    # 覆盖保存回原路径
                    cropped_img.save(screenshot_path)
                    self.add_log(LogLevel.INFO, "✓ 成功将截图裁剪为上半部分")
                    # ======================================================

                    self.add_log(LogLevel.INFO, f"个人中心截图已保存到: {screenshot_path}")
                    # 将截图路径保存到上下文，供后续组件使用
                    context.set_variable("ui_diff_compare_pic_path", screenshot_path)
                    check_saved_path = context.get_variable("ui_diff_compare_pic_path")
                    self.add_log(LogLevel.INFO, f"【Debug-1】存入上下文的截图路径是: {check_saved_path}")
                except Exception as e:
                    self.add_log(LogLevel.ERROR, f"裁剪截图失败: {e}\n{traceback.format_exc()}")
                    # 如果裁剪失败，原图还在，你可以决定是 return False 还是继续
            else:
                self.add_log(LogLevel.ERROR, "个人中心截图失败")
            return True
        except Exception as e:
            self.add_log(LogLevel.ERROR, f"进入个人中心异常: {str(e)}")
            return False