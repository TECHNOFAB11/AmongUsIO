#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import IntEnum


class AmongUsEnum(IntEnum):
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class PacketType(AmongUsEnum):
    Unreliable = 0
    Reliable = 1
    Hello = 8
    Disconnect = 9
    Acknowledgement = 10
    Fragment = 11
    Ping = 12


class MatchMakingTag(AmongUsEnum):
    HostGame = 0
    JoinGame = 1
    StartGame = 2
    RemoveGame = 3
    RemovePlayer = 4
    GameData = 5
    GameDataTo = 6
    JoinedGame = 7
    EndGame = 8
    AlterGame = 10
    KickPlayer = 11
    WaitForHost = 12
    Redirect = 13
    ReselectServer = 14
    GetGameList = 9
    GetGameListV2 = 16


class DisconnectReason(AmongUsEnum):
    ExitGame = 0
    GameFull = 1
    GameStarted = 2
    GameNotFound = 3
    IncorrectVersion = 5
    Banned = 6
    Kicked = 7
    Custom = 8
    InvalidName = 9
    Hacking = 10
    Destroy = 16
    Error = 17
    IncorrectGame = 18
    ServerRequest = 19
    ServerFull = 20
    FocusLostBackground = 207
    IntentionalLeaving = 208
    FocusLost = 209
    NewConnection = 210

    # Internal reasons from this package
    Timeout = 1000


class AlterGameTag(AmongUsEnum):
    ChangePrivacy = 1


class GameDataTag(AmongUsEnum):
    DataFlag = 1
    RpcFlag = 2
    SpawnFlag = 4
    DespawnFlag = 5
    SceneChangeFlag = 6
    ReadyFlag = 7
    ChangeSettingsFlag = 8


class RPCTag(AmongUsEnum):
    PlayAnimation = 0
    CompleteTask = 1
    SyncSettings = 2
    SetInfected = 3
    Exiled = 4
    CheckName = 5
    SetName = 6
    CheckColor = 7
    SetColor = 8
    SetHat = 9
    SetSkin = 10
    ReportDeadBody = 11
    MurderPlayer = 12
    SendChat = 13
    StartMeeting = 14
    SetScanner = 15
    SendChatNote = 16
    SetPet = 17
    SetStartCounter = 18
    EnterVent = 19
    ExitVent = 20
    SnapTo = 21
    Close = 22
    VotingComplete = 23
    CastVote = 24
    ClearVote = 25
    AddVote = 26
    CloseDoorsOfType = 27
    RepairSystem = 28
    SetTasks = 29
    UpdateGameData = 30


class SpawnTag(AmongUsEnum):
    ShipStatus0 = 0
    MeetingHud = 1
    LobbyBehavior = 2
    GameData = 3
    PlayerControl = 4
    ShipStatus1 = 5
    ShipStatus2 = 6
    ShipStatus3 = 7


class GameSettings:
    class Map(AmongUsEnum):
        """MapIds of Among Us"""

        Skeld = 0
        MiraHQ = 1
        Polus = 2
        All = 7
        # TODO: when searching for games it looks like this:
        #   Skeld = 1, MiraHQ = 2, Polus = 4
        #   thus All = Skeld | MiraHQ | Polus = 7
        #   but when receiving game data its 0, 1, 2
        #   -> create two enums??

    class Keywords(AmongUsEnum):
        """Available languages to filter by when searching for games/lobbies"""

        All = 0
        Other = 1
        Spanish = 2
        Korean = 4
        Russian = 8
        Portuguese = 16
        Arabic = 32
        Filipone = 64
        Polish = 128
        English = 256

    class TaskBarUpdate(AmongUsEnum):
        """Settings for the task bar update, for easier readability"""

        Always = 0
        Meetings = 1
        Never = 2

    class KillDistances(AmongUsEnum):
        """Kill distances, for easier readability"""

        Short = 0
        Normal = 1
        Long = 2


class PlayerAttributes:
    class Color(AmongUsEnum):
        """Player colors"""

        Red = 0
        Blue = 1
        Green = 2
        Pink = 3
        Orange = 4
        Yellow = 5
        Black = 6
        White = 7
        Purple = 8
        Brown = 9
        Cyan = 10
        Lime = 11

    class Hat(AmongUsEnum):
        """
        Among Us hats (cosmetic)
        from https://among-us.fandom.com/wiki/Cosmetics#List_of_Hats
        """

        none = 0
        Astronaut_Helmet = 1
        Backwards_Cap = 2
        Brain_Slug = 3
        Bush_Hat = 4
        Captain_Hat = 5
        Double_Top_Hat = 6
        Flowerpot_Hat = 7
        Goggles = 8
        Hard_Hat = 9
        Military_Hat = 10
        Paper_Hat = 11
        Party_Hat = 12
        Police_Hat = 13
        Stethoscope = 14
        Top_Hat = 15
        Towel_Wizard = 16
        Ushanka = 17
        Viking = 18
        Wall_Guard_Cap = 19
        Snowman = 20
        Antlers = 21
        Christmas_Lights_Hat = 22
        Santa_Hat = 23
        Christmas_Tree_Hat = 24
        Present_Hat = 25
        Candy_Canes_Hat = 26
        Elf_Hat = 27
        Yellow_Party_Hat = 28
        White_Hat = 29
        Crown = 30
        Eyebrows = 31
        Angel_Halo = 32
        Elf_Cap = 33
        Flat_Cap = 34
        Plunger = 35
        Snorkel = 36
        Henry_Figure = 37
        Safari_Hat = 38
        Sheriff_Hat = 39
        Eyeball_Lamp = 40
        Toilet_Paper_Hat = 41
        Toppat_Clan_Leader_Hat = 42
        Black_Fedora = 43
        Ski_Goggles = 44
        MIRA_Landing_Headset = 45
        MIRA_Hazmat_Mask = 46
        Medical_Mask = 47
        MIRA_Security_Cap = 48
        Straw_Hat = 49
        Banana_Hat = 50
        Beanie = 51
        Bear_Ears = 52
        Cheese_Hat = 53
        Cherry_Hat = 54
        Egg_Hat = 55
        Green_Fedora = 56
        Flamingo_Hat = 57
        Flower_Hat = 58
        Knight_Helmet = 59
        Plant_Hat = 60
        Cat_Head_Hat = 61
        Bat_Wings = 62
        Devil_Horns = 63
        Mohawk = 64
        Pumpkin_Hat = 65
        Spooky_Paper_Bag_Hat = 66
        Witch_Hat = 67
        Wolf_Ears = 68
        Pirate_Hat = 69
        Plague_Doctor_Mask = 70
        Knife_Hat = 71
        Hockey_Mask = 72
        Miner_Gear_Hat = 73
        Winter_Gear_Hat = 74
        Archaeologist_Hat = 75
        Antenna = 76
        Balloon = 77
        Bird_Nest = 78
        Black_Bandanna = 79
        Caution_Sign_Hat = 80
        Chef_Hat = 81
        CCC_Cap = 82
        Dorag = 83
        Dum_Sticky_Note = 84
        Fez = 85
        General_Hat = 86
        Pompadour = 87
        Hunter_Hat = 88
        Military_Helmet = 89
        Mini_Crewmate = 90
        Mysterious_Vagabond_Mask = 91
        Ram_Horns = 92
        Snow_Crewmate = 93
        Geoff_Keighley_Mask = 94

    class Skin(AmongUsEnum):
        """
        Among Us skins (cosmetic)
        from https://among-us.fandom.com/wiki/Cosmetics#List_of_Skins
        """

        none = 0
        Astronaut = 1
        Captain = 2
        Mechanic = 3
        Military = 4
        Police = 5
        Doctor = 6
        Black_Suit = 7
        White_Suit = 8
        Wall_Guard_Suit = 9
        MIRA_Hazmat = 10
        MIRA_Security_Guard = 11
        MIRA_Landing = 12
        Miner_Gear = 13
        Winter_Gear = 14
        Archaeologist = 15

    class Pet(AmongUsEnum):
        """
        Among Us pets (cosmetic)
        from https://among-us.fandom.com/wiki/Cosmetics#List_of_Pets
        """

        none = 0
        Brainslug = 1
        Mini_Crewmate = 2
        Dog = 3
        Henry = 4
        Hamster = 5
        Robot = 6
        UFO = 7
        Ellie = 8
        Squig = 9
        Bedcrab = 10
        Glitch = 11
