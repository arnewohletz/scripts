from ast import Add
import os
import json
from typing import Type, NamedTuple

is_gameplay = True
is_mappack = True
is_weapons = True

root_dir = "~/Library/Application Support/gzdoom/"


# class EmptyInputError(Exception):
#     """No input given"""


class Addon:
    def __init__(self, data):
        self.allow_other_addons = False
        self.iwads = ()
        self.files = ()
        self.autonomous = data["autonomous"]
        self.extending = data["extending"]
        # for key, value in data.items():
        #     setattr(self, key, value)


class Addon3323:
    allows_other_addons = False
    iwads = ()
    files = ()
    autonomous = []
    extending = []


    # def __init__(self, name, files, version=None, url=None):
    #     self.name = name
    #     self.files = files
    #     self.version = version
    #     self.url = url


    def __init__(self, data):
        if type(data) is str:
            data = json.loads(data)
        self.convert_json(data)

    def convert_json(self, data):
        self.__dict__ = {}
        for key, value in data.items():
            if type(value) is dict:
                setattr(self, key, value)
                value = Addon(value)
            self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


class Launcher:
    """
    Generates the command
    """

    def __init__(self):
        self.allows_more_current_type = False
        self.contains_weapons = False
        self.allowed_map_packs = self.get_sorted_addons(VersatileMapPack)
        self.total_conversions = self.get_sorted_addons(TotalConversion)
        self.predefined_combinations = self.get_sorted_addons(
            PredefinedCombination)
        self.gameplay_addons = self.get_sorted_addons(Gameplay)
        self.weapons_addons = self.get_sorted_addons(WeaponPack)
        self.map_packs = self.get_sorted_addons(MapPack)
        self.command = "/Applications/GZDoom.app/Contents/MacOS/gzdoom"
        print("Welcome to GZDoom Launcher!")

    def get_sorted_addons(self, class_type: Type[Addon]) -> tuple:
        addons_tuple = [cls() for cls in class_type.__subclasses__()]
        return tuple(sorted(addons_tuple, key=lambda x: x.name))

    def prompt_addon(self, text, default):
        i = input(f"{text} (Default: {default}): ")
        return i

    def print_addons(self, addon_tuple):
        for i, addon in enumerate(addon_tuple):
            if i >= 10:
                print(f"[{i}] {addon.name}")
            else:
                print(f" [{i}] {addon.name}")

    def select_addon(self, addon_tuple, last_input=False):
        self.print_addons(addon_tuple)
        addon_index = input(
            f"Select a {addon_tuple[0].type.lower()} (skipped if empty): ")
        self.allows_more_current_type = False
        if addon_index:
            addon = addon_tuple[int(addon_index)]
            self.allows_more_current_type = addon.allows_more_current_type
            self.contains_weapons = addon.contains_weapons
            for iwad in addon.iwads:
                self.command += f" -iwad {root_dir + iwad}"
            for file in addon.files:
                self.command += f" -file {root_dir + file}"
            if hasattr(addon, "allowed_map_types"):
                self.allowed_map_packs = self.get_sorted_addons(
                    addon.allowed_map_types)
            if last_input:
                self.launch()
                print("Exiting ...")
                exit(0)

    def launch(self):
        print(self.command)
        os.system(self.command)


class AutonomousAddon(Addon):
    allows_more_current_type = False
    contains_weapons = True
    total_conversions = []

    def __init__(self, data):
        super().__init__(data)
        self.total_conversions = [TotalConversion(d) for d in data.autonomous.total_conversion]


class ExtendingAddon(Addon):
    allows_other_addons = True
    contains_weapons = False


class TotalConversion:
    type = "Total Conversion"
    iwads = ("doom2.wad",)

    def __init__(self, name, version, files):
        self.name = name
        self.version = version
        self.files = files

    # def __init__(self, name, files, version=None, url=None):
    #     self.name = name
    #     self.files = files
    #     self.version = version
    #     self.url = url


class PredefinedCombination(AutonomousAddon):
    type = "Predefined Combination"


class Gameplay(ExtendingAddon):
    type = "Gameplay Addon"
    allowed_map_packs = []
    allows_brutal_doom = False
    allows_more_current_type = False
    contains_weapons = False

    def get_allowed_map_packs(self, class_type):
        addons_tuple = [cls() for cls in class_type.__subclasses__()]
        return tuple(sorted(addons_tuple, key=lambda x: x.name))


class WeaponPack(ExtendingAddon):
    type = "Weapon Pack"
    contains_weapons = True
    allows_more_current_type = False


class MapPack(ExtendingAddon):
    type = "Map Pack"
    allows_more_current_type = False


class VersatileMapPack(MapPack):
    iwads = ("doom2.wad",)


class AshesEpisode1(TotalConversion):
    name = "Ashes Episode 1 - 2063"
    version = "2.23"
    files = ("ashes/AshesSAMenu.pk3",
             "ashes/Ashes2063Enriched2_23.pk3",
             "ashes/Ashes2063EnrichedFDPatch.pk3")


class AshesEpisode2(TotalConversion):
    name = "Ashes Episode 2 - Afterglow"
    version = "1.10"
    files = ("ashes/AshesSAMenu.pk3",
             "ashes/AshesAfterglow1_10.pk3")


class Asterodead(TotalConversion):
    name = "Asterodead"
    version = "20220924"
    files = ("ASTERODEAD_V20220924.pk3",)


class BladeOfAgony(TotalConversion):
    name = "Blade Of Agony"
    version = "3.1"
    iwads = ("boa.ipk3",)


class BrutalDoom64(TotalConversion):
    name = "Brutal Doom 64"
    version = "2.5"
    files = ("Brutal_Doom_64_v2.5_u30.12/bd64game_v2.5.pk3",
             "Brutal_Doom_64_v2.5_u30.12/bd64maps_v2.5.pk3")


class BrutalHeretic(TotalConversion):
    name = "Brutal Heretic"
    version = "5.0"
    url = "https://nzdoom.net/printthread.php?tid=3"
    iwads = ("heretic.wad",)
    files = ("brutal_heretic/H20MUS.wad",
             "brutal_heretic/BrutalHereticRPG_V5.0.pk3",
             "brutal_heretic/heretic_gz.pk3")


class BrutalHexen(TotalConversion):
    name = "Brutal Hexen"
    version = "7.5"
    url = "https://nzdoom.net/showthread.php?tid=2"
    iwads = ("hexen.wad",)
    files = ("brutal_hexen/3_HEXEN64.wad",
             "brutal_hexen/damnums_1.0.2.pk3",
             "brutal_hexen/hexen_gz.pk3",
             "brutal_hexen/Resurrectupdate.pk3",
             "brutal_hexen/GatherYourParty.pk3",
             "brutal_hexen/BrutalHexenRPG_V7.5.pk3")


class BrutalWolfenstein3D(TotalConversion):
    name = "Brutal Wolfenstein 3D"
    version = "6.0"
    files = ("ZMC-BW6.0.pk3",)


class Doom64Retribution(TotalConversion):
    name = "Doom 64 - Retribution"
    version = "1.5"
    iwads = ()
    files = ("D64RTRv1.5/D64RTR_v1.5.WAD",)


class GoldenSouls(TotalConversion):
    name = "Golden Souls 2"
    version = "1.4"
    files = ("GoldenSouls2_1.4.pk3",)


class Pirate(TotalConversion):
    name = "PirateDoom"
    version = "1.8.5"
    files = ("Pirates.wad",)


class TotalChaos(TotalConversion):
    name = "Total Chaos"
    version = "1.40"
    files = ("total_chaos/totalchaos.pk3",
             "total_chaos/zd_extra.pk3 +set gl_precache 1")


class WolfensteinX(TotalConversion):
    name = "Wolfenstein X"
    version = "Final"
    files = ("WolfensteinX_HeartsOfLibertyFinalEditionFix/WolfX_v2.pk3",
             "WolfensteinX_HeartsOfLibertyFinalEditionFix/WolfX_heartsofliberty-finaledition-fix.pk3")


class HexenHD(PredefinedCombination):
    name = "Hexen HD"
    iwads = ("hexen.wad",)
    files = ("hexen_hd/h_PBR_v461.pk3",
             "hexen_hd/HEXENREMADE.wad",
             "hexen_hd/Hexen_HQ_Sounds.pk3",
             "hexen_hd/hexen_gz_v4.pk3",
             "hexen_hd/Universal_Rain_and_Snow.pk3",
             "hexen_hd/HexenI7MusV3.pk3",
             "hexen_hd/nashgore.pk3")


class BrutalDoom(Gameplay):
    name = "Brutal Doom (CE)"
    version = "21.12.3"
    url = "https://github.com/BLOODWOLF333/Brutal-Doom-Community-Expansion"
    allows_more_current_type = True
    files = ("brutalv21.12.3HF.pk3",)


class BrutalDoomExtendedEdition(Gameplay):
    name = "Brutal Doom Extended Edition"
    version = "9.0"
    url = "https://www.moddb.com/mods/brutal-doom-extended-edition"
    allows_more_current_type = True
    files = (
        "Brutal_Doom_Extended_Edition_v9.0/Brutal_Doom_Extended_Edition.pk3",
        "Brutal_Doom_Extended_Edition_Community_Weapons_Pack.pk3",
        "Brutal_Doom_Extended_Edition_HXRTC_Hud.pk3")


class BrutalTrailblazer(Gameplay):
    name = "Brutal Trailblazer"
    version = "1.5e"
    url = "https://forum.zdoom.org/viewtopic.php?t=56465&hilit=brutal+trailblazer"
    contains_weapons = True
    files = ("Brutal_Trailblazer_1.5e/bd21monstersonlyfix.pk3",
             "Brutal_Trailblazer_1.5e/Trailblazer.pk3",
             "Brutal_Trailblazer_1.5e/Brutal Trailblazer Patch v1.5e.pk3")


class DarkForcesMusic(Gameplay):
    name = "Dark Forces Music"
    version = "Feb 14th, 2020"
    url = "https://www.moddb.com/downloads/dark-forces-music-patch"
    allows_more_current_type = True
    allows_brutal_doom = True
    files = ("DarkForcesMusicX.pk3",)


class DN3Doom(Gameplay):
    name = "DN3Doom (Duke Nukem Style)"
    allowed_map_packs = []
    contains_weapons = True
    version = "1.07b"
    files = ("DN3DoomDuke_Nukem3D_FullMusics.wad",
             "DN3Doom/Duke_Music_and_Textures.pk3",
             "DN3Doom/Duke_SiN_mod.zip",
             "DN3Doom/Hd_Sounds.pk3",
             "DN3Doom/SpriteShadow_v2.pk3",
             "DN3Doom/DN3DMP5K.pk3",
             "DN3Doom/DN3DoomAltPC.pk3",
             "DN3Doom/DN3DooM.pk3")


class DoomEnhanced(Gameplay):
    name = "Doom Enhanced"
    version = ""
    allows_more_current_type = True
    allows_brutal_doom = True
    files = ("doom_enhanced/CustomSounds.pk3",
             "doom_enhanced/HDObjects.pk3",
             "doom_enhanced/HDTextures.pk3",
             "doom_enhanced/Materials.pk3")


class HighQualityPSXMusic(Gameplay):
    name = "High Quality PSX Music (Slow, Gloomy)"
    version = "Jun 9th, 2015"
    allows_more_current_type = True
    allows_brutal_doom = True
    files = ("music/HQPSXMUS.WAD",)


class LambdaStrike(Gameplay):
    name = "Lambda Strike"
    version = "1.0.5"
    contains_weapons = True
    files = ("Lambda-Strike1_0_5/Lambda-Strike_Resources.pk3",
             "Lambda-Strike1_0_5/Lambda-Strike_Code.pk3",
             "Lambda-Strike1_0_5/Lambda-Strike_HD.pk3")


class MapsOfChaosOverkill(Gameplay):
    name = "Maps Of Chaos - Overkill"
    version = ""
    allows_more_current_type = True
    files = ("mapsofchaos-ok.wad",)


class PainkillerMutilation(Gameplay):
    name = "Painkiller Mutilator (Enemies & Weapons)"
    version = "1.7"
    contains_weapons = True
    files = ("painkiller_mutilator/Painkiller_Monsters.pk3",
             "painkiller_mutilator/Painkiller_Weapons_3D.pk3")


class ProjectBrutality(Gameplay):
    name = "Project Brutality"
    version = "3.0"
    url = "https://github.com/pa1nki113r/Project_Brutality"
    allows_brutal_doom = False
    contains_weapons = True
    files = ("Project_Brutality-master.zip",)


class VoxelDoom(Gameplay):
    name = "Voxel Doom"
    version = "1.0"
    allowed_map_packs = []
    contains_weapons = True
    files = ("cheello_voxels.zip",)


class WoomyProjectPetersen(Gameplay):
    name = "Woomy: Project Petersen (includes "
    version = "2.7"
    contains_weapons = True
    files = ("WOOMY_Project_Petersen.pk3",
             "Meat_Grinder_Enemies.pk3")


class XimStarWarsMapPack(MapPack):
    pass


class XimStarWars(Gameplay):
    name = "Xim's Star Wars"
    version = "2.9.2"
    contains_weapons = True
    allowed_map_types = XimStarWarsMapPack

    files = ("Xim-StarWars/Maps/DarkHour.wad",
             "Xim-StarWars/Xim-StarWars-v2.9.2.pk3",
             "Xim-StarWars/Xim-StarWarsProps.pk3",
             "Xim-StarWars/Xim-StarWarsTextures-v2.1.pk3",
             "Xim-StarWars/Xim-StarWars-FreeMP3.pk3")


class CallOfDoomBlackWarfare(WeaponPack):
    name = "Call Of Doom - Black Warfare (Brutal Doom Version)"
    version = "2.0"
    files = ("CODBW_FileA_Brutal_v2.pk3",
             "CODBW_FileB_HD_v2.pk3")


class PainkillerMutilatorWeaponsOnly(WeaponPack):
    name = "Painkiller Mutilator"
    version = "1.7"
    files = ("painkiller_mutilator/Painkiller_Weapons_3D.pk3",)


class Doom(VersatileMapPack):
    name = "Doom"
    iwads = ("doom.wad",)


class Doom2(VersatileMapPack):
    name = "Doom 2"
    iwads = ("doom2.wad",)


class Doom2MasterLevels(VersatileMapPack):
    name = "Doom 2 - Master Levels"
    files = ("DOOM2_THE_MASTER_LEVELS.pk3",)


class Doom2NoRestForTheLiving(VersatileMapPack):
    name = "Doom 2 - No Rest for the Living"
    files = ("NERVE.wad",)


class DragonSektorRemake(VersatileMapPack):
    name = "Dragon Sektor Remake"
    version = "0.43"
    url = "https://www.moddb.com/mods/dragon-sector-the-remake"
    files = ("dragon-sector-remake-v0.43.pk3",)


class FinalDoom(VersatileMapPack):
    name = "Final Doom - TNT: Evilution"
    iwads = ("TNT.wad",)


class PlutoniaExperiment(VersatileMapPack):
    name = "Final Doom - Plutonia Experiment"
    iwads = ("plutonia.wad",)


class Sigil(VersatileMapPack):
    name = "Sigil a.k.a. Doom - Episode 5"
    files = ("SIGIL_v1_21.wad")
    iwads = ("doom.wad",)


# class BackToSaturnX(XimStarWarsMapPack):
#     name = "Return To Saturn X"
#     version = "1.1.6"
#     url = "https://www.doomworld.com/idgames/levels/doom2/megawads/btsx_e1"
#     files = ("Xim-StarWars/Maps/btsx_e1a.wad",
#              "Xim-StarWars/Maps/btsx_e1b.wad")


class DarkHour(XimStarWarsMapPack):
    name = "Dark Hour"
    version = "2001.08.06"
    url = "https://www.doomworld.com/idgames/levels/doom2/Ports/d-f/darkhour"
    files = ("Xim-StarWars/Patches/Xim-StarWarsDarkHour.pk3",
             "Xim-StarWars/Maps/DarkHour.wad",)


class GoingDown(XimStarWarsMapPack):
    name = "Going Down"
    version = "2014.02.14"
    url = "https://www.doomworld.com/idgames/levels/doom2/Ports/megawads/gd"
    files = ("Xim-StarWars/Maps/gd.wad",)


class SpacWars(XimStarWarsMapPack):
    name = "Spacwars"
    version = "2015.09.01"
    url = "https://www.doomworld.com/idgames/levels/doom2/Ports/s-u/spacwars"
    files = ("Xim-StarWars/Patches/Xim-StarWarsSpacwars.pk3",
             "Xim-StarWars/Maps/DarkHour.wad",)


class StarWarsDoom2(XimStarWarsMapPack):
    name = "Dark Encounters"
    version = "Re-release/bugfix 2019"
    url = "https://www.doomworld.com/idgames/levels/doom2/Ports/megawads/drkenctr"
    files = ("Xim-StarWars/Maps/drkenctr.wad",)


if __name__ == "__main__":

    with open("addons.json") as file:
        data = json.load(file)

    addons = Addon(data)
    total_conversions = addons.autonomous.total_conversions
    predefined_combinations = PredefinedCombination(data)
    autonomous_addons = AutonomousAddon(addons.autonomous_addon)

    # launcher = Launcher()
    # launcher.select_addon(launcher.total_conversions, True)
    # launcher.select_addon(launcher.predefined_combinations, True)
    # launcher.select_addon(launcher.gameplay_addons, False)
    # while launcher.allows_more_current_type:
    #     # TODO: Add list only combinable gameplay mods
    #     launcher.select_addon(launcher.gameplay_addons, False)
    # if not launcher.contains_weapons:
    #     launcher.select_addon(launcher.weapons_addons, False)
    # # launcher.select_addon(launcher.map_packs, True)
    # launcher.select_addon(launcher.allowed_map_packs, True)
