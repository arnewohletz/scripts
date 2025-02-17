import json
import os
import subprocess


ADDON_ROOT_DIR = "~/Library/Application\\ Support/gzdoom/"


class Launcher:

    def __init__(self):

        with open(os.path.dirname(__file__) + "/addons.json", "r") as file:
            (
                self.gzdoom_versions,
                self.total_conversions,
                self.predefined_combinations,
                self.gameplay_mods,
                self.weapon_packs,
                self.map_packs,
                self.live_through_doom_map_pack,
                self.xim_star_wars_map_pack
            ) = self.json_to_addon_objects(json.loads(file.read()))

        self.allowed_map_packs = self.map_packs
        self.contains_weapons = False
        self.iwad_defined = False

        print("Welcome to GZDoom Launcher!")

        self.select_gzdoom_version(self.gzdoom_versions)
        self.select_addon(self.total_conversions, True)
        self.select_addon(self.predefined_combinations, True)
        self.select_addon(self.gameplay_mods, False)
        while self.allows_more_current_type:
            self.select_addon(self.gameplay_mods, False)
        if not self.contains_weapons:
            self.select_addon(self.weapon_packs, False)
        self.select_addon(self.allowed_map_packs, True)

    def json_to_addon_objects(self, json_data):
        return (
            [GZDoomVersion(**data)
                for data in json_data["gzdoom_version"]],
            [TotalConversion(**data)
                for data in json_data["total_conversion"]],
            [PredefinedCombination(**data)
                for data in json_data["predefined_combination"]],
            [Gameplay(**data)
                for data in json_data["gameplay_mod"]],
            [WeaponPack(**data)
                for data in json_data["weapon_pack"]],
            [MapPack(**data) 
                for data in json_data["map_pack"]],
            [LiveThroughDoomMapPack(**data)
                for data in json_data["live_through_doom_map_pack"]],
            [XimStarWarsMapPack(**data)
                for data in json_data["xim_star_wars_map_pack"]]
        )

    def select_gzdoom_version(self, gzdoom_versions_tuple):
        get_default_version_cmd = [
            "defaults", "read",
            "/Applications/GZDoom.app/Contents/Info.plist",
            "CFBundleShortVersionString"
        ]
        raw_default_version = subprocess.check_output(get_default_version_cmd)
        default_version = raw_default_version.decode(
            "utf-8").strip("\n").replace("g", "")
        for i, version in enumerate(gzdoom_versions_tuple):
            print(f"{' '*(3 - len(str(i)))}[{i}] {version.name}", end=" ")
            if version.name == "default":
                print(f"({default_version})")
            else:
                print("")
        gzdoom_version_index = input(
            f"Select a {gzdoom_versions_tuple[0].type} (default, if empty): "
        )
        if gzdoom_version_index:
            gzdoom_version = gzdoom_versions_tuple[int(gzdoom_version_index)]
            self.command = gzdoom_version.path
        else:
            self.command = "/Applications/GZDoom.app/Contents/MacOS/gzdoom"

    def select_addon(self, addon_tuple, last_input=False):
        print_addons(addon_tuple)
        addon_index = input(
            f"Select a {addon_tuple[0].type} (skipped, if empty): "
        )
        self.allows_more_current_type = False
        if addon_index:
            addon = addon_tuple[int(addon_index)]
            self.allows_more_current_type = addon.allows_more_current_type
            self.contains_weapons = addon.contains_weapons
            if hasattr(addon, "iwads") and not self.iwad_defined:
                for iwad in addon.iwads:
                    self.command += f" -iwad {ADDON_ROOT_DIR + iwad}"
                self.iwad_defined = True
            if hasattr(addon, "files"):
                for file in addon.files:
                    self.command += f" -file {ADDON_ROOT_DIR + file}"
            if hasattr(addon, "allowed_map_packs"):
                print(addon.allowed_map_packs)
                with open(os.path.dirname(__file__)
                          + "/addons.json", "r") as file:
                    if addon.allowed_map_packs == "live_through_doom_map_pack":
                        self.allowed_map_packs = \
                            self.live_through_doom_map_pack
                    if addon.allowed_map_packs == "xim_star_wars_map_pack":
                        self.allowed_map_packs = self.xim_star_wars_map_pack
            if last_input:
                if not self.iwad_defined:
                    self.command += f" -iwad {ADDON_ROOT_DIR}doom2.wad"
                self.launch()
                print("Exiting ...")
                exit(0)

    def launch(self):
        print(self.command)
        os.system(self.command)


def print_addons(addons_tuple) -> None:
    for i, addon in enumerate(addons_tuple):
        if hasattr(addon, "version"):
            print(f"{' '*(3 - len(str(i)))}[{i}] {addon.name} "
                  f"(v{addon.version}) "
                  f"{addon.rating * '\N{LARGE GREEN CIRCLE}'}"
                  f"{(5 - addon.rating) * '\N{LARGE RED CIRCLE}'}")
        else:
            print(f"{' '*(3 - len(str(i)))}[{i}] {addon.name} "
                  f"{addon.rating * '\N{LARGE GREEN CIRCLE}'}"
                  f"{(5 - addon.rating) * '\N{LARGE RED CIRCLE}'}")


class GZDoomVersion(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.type = "GZDoom version"


class Addon(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class AutonomousAddon(Addon):

    def __init__(self, **kwargs):
        self.allows_more_current_type = False
        self.contains_weapons = True
        self.iwads = ["doom2.wad"]
        super(AutonomousAddon, self).__init__(**kwargs)


class ExtendingAddon(Addon):

    def __init__(self, **kwargs):
        super(ExtendingAddon, self).__init__(**kwargs)
        self.allows_more_current_type = True
        self.contains_weapons = False


class TotalConversion(AutonomousAddon):

    def __init__(self, **kwargs):
        super(TotalConversion, self).__init__(**kwargs)
        self.type = "Total Conversion"


class PredefinedCombination(AutonomousAddon):

    def __init__(self, **kwargs):
        super(PredefinedCombination, self).__init__(**kwargs)
        self.type = "Predefined Combination"


class Gameplay(ExtendingAddon):

    def __init__(self, **kwargs):
        super(Gameplay, self).__init__(**kwargs)
        self.type = "Gameplay Mod"


class WeaponPack(ExtendingAddon):

    def __init__(self, **kwargs):
        super(WeaponPack, self).__init__(**kwargs)
        self.type = "Weapon Pack"


class MapPack(ExtendingAddon):

    def __init__(self, **kwargs):
        super(MapPack, self).__init__(**kwargs)
        self.type = "Map Pack"


class LiveThroughDoomMapPack(MapPack):

    def __init__(self, **kwargs):
        super(LiveThroughDoomMapPack, self).__init__(**kwargs)
        self.type = "Live Through Doom Map Pack"


class XimStarWarsMapPack(MapPack):

    def __init__(self, **kwargs):
        super(XimStarWarsMapPack, self).__init__(**kwargs)
        self.type = "Xim Star Wars Map Pack"


if __name__ == "__main__":

    launcher = Launcher()
