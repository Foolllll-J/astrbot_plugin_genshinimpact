import random
import time
from typing import List, Dict, Optional
from astrbot import logger
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.event.filter import event_message_type, EventMessageType

@register("astrbot_plugin_genshinimpact", "ましろSaber&Foolllll", "一个原神启动插件", "1.4", "https://github.com/Foolllll-J/astrbot_plugin_genshinimpact")
class GenshinImpactPlugin(Star):
    def __init__(self, context: Context, config: Optional[Dict] = None):
        super().__init__(context)
        self.config = config if config else {}
        self.group_whitelist: List[int] = self.config.get("group_whitelist", [])
        self.group_whitelist = [int(gid) for gid in self.group_whitelist]
        self.ys_quotes: List[str] = self.config.get("ys_quotes", [])
        self.cooldown: int = self.config.get("cooldown", 0)
        self.ignore_cooldown_on_exact_match: bool = self.config.get("ignore_cooldown_on_exact_match", False)
        self.last_trigger_time: Dict[str, float] = {}  # 存储每个群的最后触发时间

    @event_message_type(EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent) -> MessageEventResult:
        """
        当消息中包含"原神"时随机发送一条圣经。
        """
        group_id_str = event.get_group_id()
        if group_id_str:  # 如果是群聊
            group_id = int(group_id_str)
            if self.group_whitelist and group_id not in self.group_whitelist:
                return
        # 如果是私聊，则不检查白名单

        msg_obj = event.message_obj
        text = msg_obj.message_str or ""

        if "原神" in text and not event.is_at_or_wake_command:
            # 检查是否完全匹配“原神”
            is_exact_match = text.strip() == "原神"

            # 检查冷却时间
            session_id = msg_obj.session_id
            current_time = time.time()
            
            # 如果配置了完全匹配时无视冷却，且当前是完全匹配，则跳过冷却检查
            skip_cooldown = self.ignore_cooldown_on_exact_match and is_exact_match

            if not skip_cooldown and self.cooldown > 0 and session_id in self.last_trigger_time:
                elapsed = current_time - self.last_trigger_time[session_id]
                if elapsed < self.cooldown:
                    logger.debug(f"原神触发被冷却限制，剩余冷却时间：{self.cooldown - elapsed:.1f}秒")
                    return
            
            # 检查是否有配置的语录
            if not self.ys_quotes:
                logger.warning("原神语录列表为空，插件将不会回复")
                return
            
            # 更新最后触发时间
            self.last_trigger_time[session_id] = current_time
            
            # 随机抽取一条圣经
            selected_text = random.choice(self.ys_quotes)
            yield event.plain_result(selected_text)
