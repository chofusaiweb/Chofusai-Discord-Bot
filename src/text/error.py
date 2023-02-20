from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorText:
    CHANNEL_NOT_FOUND = "チャンネルが見つかりませんでした。"
    CHANNEL_OR_MESSAGE_NOT_FOUND = "チャンネルまたはメッセージが見つかりませんでした。"

    FAILED_TO_PIN = "ピン留めに失敗しました。\n既にチャンネルに50個以上のピン留めがある可能性があります。"
    FAILED_TO_UNARCHIVE = "アーカイブの解除に失敗しました。"
    FAILED_TO_UNPIN = "ピン留めの解除に失敗しました。"
    FAILED_TO_SEND_DM = "DMの送信に失敗しました。\n送信対象がDMが受信できない設定に\nしている可能性があります。"

    FORBIDDEN = "必要な権限がBotに与えられていません。"

    UNKNOWN_ERROR = "不明なエラーが発生しました。"
