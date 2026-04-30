"""个人中心激励广告触发策略"""
import asyncio
from typing import Dict, Any
from automation_engine.components.helpers.strategy_base import StrategyBase
from automation_engine.context.execution import ExecutionContext
from automation_engine.definitions import LogLevel
from automation_engine.definitions.exceptions.entry_chain_errors import FindAdError
from automation_engine.drivers.base import LocatorStrategy


class SecondRewardTrigger(StrategyBase):
    """
    激励二级页广告触发策略 - 进入个人中心页点击挂件触发
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

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> bool:
        """
        激励二级页广告触发策略：
        入口：【免费看挂件-reward_widget】
        Args:
            inputs: 输入参数
            context: 执行上下文

        Returns:
            bool: 是否触发成功
        """
        try:
            ops = context.get_operations()
            platform = inputs.get("platform", "android").lower()
            await asyncio.sleep(5)
            await self.helper.click_first_page(ops)
            await self.helper.enter_person_center(ops)
            await self.helper.close_login_popup(ops)

            success = False
            click_state = await self._click_widget(ops)
            if click_state == 1:
                success = await self._entry_second_first(ops)
            elif click_state == 2:
                success = await self._entry_second_second(ops)
            else:
                self.add_log(LogLevel.ERROR, "进入激励广告二级页失败")
            if success:
                return True
            return False
        except Exception as e:
            self.add_log(LogLevel.ERROR, f"激励广告二级页触发失败: {str(e)}")
            raise FindAdError()

    async def _click_widget(self,ops)->int:
        """
        点击免费看挂件
        0 ———— 没找到挂件
        1 ———— 首次“免费看”挂件
        2 ———— 非首次,“续时长”挂件
        """
        self.add_log(LogLevel.INFO,"尝试查找免费看挂件")
        widget_element = await ops.find_by_text(text = "免费看",
                                          strategy_priority = [LocatorStrategy.TEXT.value,LocatorStrategy.OCR_TEXT.value],
                                          timeout = 1)
        if widget_element:
            await widget_element.click()
            return 1

        if not widget_element :
            widget_element = await ops.find_by_text(text="续时长",
                                                    strategy_priority=[LocatorStrategy.TEXT.value,LocatorStrategy.OCR_TEXT.value],
                                                    timeout=1)
            if widget_element:
                await widget_element.click()
                return 2
        return 0


    async def _exit_first_ad(self,ops)->bool:
        """
        1、右滑
        2、点击退出广告
        3、点X
        点击放弃领取退出
        """
        #步骤1:右滑
        try:
            screen_size = await ops.get_window_size()
            if not screen_size:
                self.add_log(LogLevel.ERROR,"获取屏幕尺寸失败")
                return False
            width,height = screen_size
            await asyncio.sleep(1)
            start_x = int(width * 0.01)
            start_y = int(height*0.5)
            end_x = int(width*0.8)
            end_y = int(height*0.5)
            self.add_log(LogLevel.INFO,"滑动退出广告")
            await ops.swipe(start_x,start_y,end_x,end_y,duration=800)

            # 步骤2:点击放弃领取
            exit_button = await ops.find_by_text(text="放弃领取",
                                                 strategy_priority = [LocatorStrategy.TEXT.value,LocatorStrategy.OCR_TEXT.value],
                                                 timeout=3)
            if exit_button:
                self.add_log(LogLevel.INFO,"点击放弃领取")
                await exit_button.click()
                await asyncio.sleep(2)
                return True
            self.add_log(LogLevel.WARNING,"未找到放弃领取，尝试点击退出广告")
            close_button = await ops.find_by_text(text="退出广告",
                                                  strategy_priority=[LocatorStrategy.TEXT.value,LocatorStrategy.OCR_TEXT.value],
                                                  timeout=3)
            if not close_button:
                close_button = await ops.find_by_text(text="退出广告",
                                                      strategy_priority=[LocatorStrategy.TEXT.value,LocatorStrategy.OCR_TEXT.value],
                                                      timeout=3)
            if close_button:
                self.add_log(LogLevel.INFO,"点击关闭按钮退出广告")
                await close_button.click()
                await asyncio.sleep(2)
                return True
            return False
        except Exception as e:
            self.add_log(LogLevel.ERROR, f"退出广告异常: {str(e)}")
            return False

    async def _entry_second_first(self,ops):
        self.add_log(LogLevel.INFO, "入口点击成功，等待广告弹窗渲染...")
        await asyncio.sleep(5)
        self.add_log(LogLevel.INFO, "退出初始广告进入二级页")
        await asyncio.sleep(5)
        exit_success = await self._exit_first_ad(ops)
        if exit_success:
            second_success = await ops.find_ocr_text_and_point(text="看广告续时长",
                                                               timeout=5.0,  # 减少超时时间到5秒
                                                               accurate=False,  # 优先使用模糊匹配
                                                               index=0)
            if second_success:
                return True
            if not second_success:
                self.add_log(LogLevel.ERROR, "❌进入二级页失败")
                return False
        return False
    async def _entry_second_second(self,ops):
        self.add_log(LogLevel.INFO, "第二次进入二级页，等待渲染...")
        await asyncio.sleep(5)
        second_success = await ops.find_by_text(text="看广告续时长",
                                                    strategy_priority=[LocatorStrategy.TEXT.value,
                                                                       LocatorStrategy.OCR_TEXT.value],
                                                    timeout=1)
        if second_success:
            return True
        if not second_success:
            self.add_log(LogLevel.ERROR, "❌进入二级页失败")
            return False
        return False

