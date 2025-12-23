from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal

StatusType = Literal['online', 'idle', 'dnd', 'invisible']

### --- Guild Payloads --- ###

@dataclass
class JoinGuildPayload:
    invite_code: str
    token: str
    context: Optional[str] = None


@dataclass
class LeaveGuildPayload:
    guild_id: str
    token: str


@dataclass
class GetGuildPayload:
    guild_id: str
    token: str


@dataclass
class GetGuildChannelsPayload:
    guild_id: str
    token: str


@dataclass
class GetGuildRolesPayload:
    guild_id: str
    token: str


@dataclass
class GetGuildEmojisPayload:
    guild_id: str
    token: str


@dataclass
class GetGuildInvitesPayload:
    guild_id: str
    token: str


@dataclass
class CreateGuildPayload:
    name: str
    token: str
    icon: Optional[str] = None
    channels: Optional[List[Dict[str, Any]]] = None
    system_channel_id: Optional[str] = None
    guild_template_code: Optional[str] = None


@dataclass
class DeleteGuildPayload:
    guild_id: str
    token: str


### --- Reaction Payloads --- ###


@dataclass
class AddReactionPayload:
    channel_id: str
    message_id: str
    emoji: str
    token: str

@dataclass
class AddSuperReactionPayload:
    channel_id: str
    message_id: str
    emoji: str
    token: str

@dataclass
class RemoveReactionPayload:
    channel_id: str
    message_id: str
    emoji: str
    token: str
    user_id: Optional[str] = None


@dataclass
class GetReactionUsersPayload:
    channel_id: str
    message_id: str
    emoji: str
    token: str
    limit: Optional[int] = 50
    after: Optional[str] = None


@dataclass
class ClearReactionsPayload:
    channel_id: str
    message_id: str
    token: str
    emoji: Optional[str] = None


### --- Message Payloads --- ###


@dataclass
class CreateMessagePayload:
    channel_id: str
    content: str
    token: str

    tts: bool = False
    nonce: Optional[str] = None


@dataclass
class EditMessagePayload:
    channel_id: str
    message_id: str
    token: str

    content: Optional[str] = None


@dataclass
class DeleteMessagePayload:
    channel_id: str
    message_id: str
    token: str


@dataclass
class ReplyMessagePayload:
    channel_id: str
    message_id: str
    content: str
    token: str

    mention_author: bool = True


@dataclass
class ForwardMessagePayload:
    from_channel_id: str
    to_channel_id: str
    message_id: str
    guild_id: str
    token: str


@dataclass
class CreatePollPayload:
    channel_id: str
    token: str

    question: str
    answers: List[str]
    duration_hours: int = 24
    allow_multiple: bool = False
    tts: bool = False


@dataclass
class PinMessagePayload:
    channel_id: str
    message_id: str
    token: str


@dataclass
class UnpinMessagePayload:
    channel_id: str
    message_id: str
    token: str


@dataclass
class TriggerTypingPayload:
    channel_id: str
    token: str


### --- Boost Payloads --- ###


@dataclass
class GetBoostSlotsPayload:
    token: str


@dataclass
class BoostGuildPayload:
    guild_id: str
    token: str

    subscription_slot_ids: List[str]


@dataclass
class RemoveGuildBoostPayload:
    guild_id: str
    token: str

    subscription_slot_ids: List[str]


### --- Member Payloads --- ###
@dataclass
class KickMemberPayload:
    guild_id: str
    user_id: str
    token: str
    reason: Optional[str] = None


@dataclass
class BanMemberPayload:
    guild_id: str
    user_id: str
    token: str
    reason: Optional[str] = None
    delete_message_days: Optional[int] = 0


@dataclass
class TimeoutMemberPayload:
    guild_id: str
    user_id: str
    token: str
    duration_seconds: int


@dataclass
class MuteMemberPayload:
    guild_id: str
    user_id: str
    token: str
    mute: bool


@dataclass
class DeafenMemberPayload:
    guild_id: str
    user_id: str
    token: str
    deafen: bool


@dataclass
class ChangeNickMemberPayload:
    guild_id: str
    user_id: str
    token: str
    nick: str


### --- User Payloads --- ###


@dataclass
class GetUserPayload:
    token: str


@dataclass
class EditAvatarPayload:
    token: str
    avatar: str


@dataclass
class EditUsernamePayload:
    token: str
    username: str
    password: str


@dataclass
class EditGlobalNamePayload:
    token: str
    global_name: Optional[str]


@dataclass
class EditBioPayload:
    token: str
    bio: str


@dataclass
class ChangeStatusPayload:
    token: str
    custom_text: str
    status_type: Optional[StatusType] = "dnd"
    
@dataclass
class EditClanTagPayload:
    token: str
    identity_guild_id: str
    identity_enabled: bool = True


@dataclass
class ChangeLanguagePayload:
    token: str
    locale: str


@dataclass
class ChangeAppearancePayload:
    token: str
    theme: str


@dataclass
class ChangePasswordPayload:
    token: str
    old_password: str
    new_password: str


### --- Thread Payloads --- ###


@dataclass
class CreateThreadPayload:
    channel_id: str
    name: str
    token: str

    auto_archive_duration: int = 1440
    type: int = 11
    invitable: bool = True


@dataclass
class DeleteThreadPayload:
    thread_id: str
    token: str


### --- Forum Payloads --- ###


@dataclass
class CreateForumPayload:
    channel_id: str
    name: str
    token: str
    content: str

    auto_archive_duration: int = 1440
    type: int = 11
    invitable: bool = True


@dataclass
class FollowPostPayload:
    post_id: str
    token: str


@dataclass
class UnfollowPostPayload:
    post_id: str
    token: str


@dataclass
class JSONPayload:
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data
