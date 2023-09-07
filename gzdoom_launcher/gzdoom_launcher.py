import json
import os


is_gameplay = True
is_mappack = True
is_weapons = True

root_dir = "~/Library/Application\ Support/gzdoom/"


class Launcher:

    def __init__(self):

        with open(os.path.dirname(__file__) + "/addons.json", "r") as file:
            (self.total_conversions,
             self.predefined_combinations,
             self.gameplay_mods,
             self.weapon_packs,
             self.map_packs,
             self.xim_star_wars_map_pack) = self.json_to_addon_objects(
                 json.loads(file.read()))

        self.allowed_map_packs = self.map_packs
        self.contains_weapons = False
        self.iwad_defined = False
        self.command = "/Applications/GZDoom.app/Contents/MacOS/gzdoom"
        print("Welcome to GZDoom Launcher!")

    def json_to_addon_objects(self, json_data):
        return (
            [TotalConversion(**data) for data in json_data["total_conversion"]],
            [PredefinedCombination(**data) for data in json_data["predefined_combination"]],
            [Gameplay(**data) for data in json_data["gameplay_mod"]],
            [WeaponPack(**data) for data in json_data["weapon_pack"]],
            [MapPack(**data) for data in json_data["map_pack"]],
            [XimStarWarsMapPack(**data) for data in json_data["xim_star_wars_map_pack"]]
        )

    def select_addon(self, addon_tuple, last_input=False):
        print_addons(addon_tuple)
        addon_index = input(
            f"Select a {addon_tuple[0].type} (skipped, if empty): ")
        self.allows_more_current_type = False
        if addon_index:
            addon = addon_tuple[int(addon_index)]
            self.allows_more_current_type = addon.allows_more_current_type
            self.contains_weapons = addon.contains_weapons
            if hasattr(addon, "iwads") and not self.iwad_defined:
                for iwad in addon.iwads:
                    self.command += f" -iwad {root_dir + iwad}"
                self.iwad_defined = True
            if hasattr(addon, "files"):
                for file in addon.files:
                    self.command += f" -file {root_dir + file}"
            if hasattr(addon, "allowed_map_packs"):
                print(addon.allowed_map_packs)
                with open(os.path.dirname(__file__) + "/addons.json", "r") as file:
                    if (addon.allowed_map_packs == "xim_star_wars_map_pack"):
                        self.allowed_map_packs = self.xim_star_wars_map_pack
            if last_input:
                if not self.iwad_defined:
                    self.command += f" -iwad {root_dir}doom2.wad"
                self.launch()
                print("Exiting ...")
                exit(0)

    def launch(self):
        print(self.command)
        os.system(self.command)


def print_addons(addons_tuple) -> None:
    for i, addon in enumerate(addons_tuple):
        if hasattr(addon, "version"):
            print(f"{' '*(3 - len(str(i)))}[{i}] {addon.name} (v{addon.version})") 
        else:
            print(f"{' '*(3 - len(str(i)))}[{i}] {addon.name}") 


class AutonomousAddon(object):

    def __init__(self):
        self.allows_more_current_type = False
        self.contains_weapons = True
        self.iwads = ["doom2.wad"]


class ExtendingAddon(object):

    def __init__(self):
        self.allows_more_current_type = True
        self.contains_weapons = False
        self.allowed_map_packs = MapPack


class TotalConversion(AutonomousAddon):

    def __init__(self, name, version, files, **kwargs):
        super(TotalConversion, self).__init__()
        self.name = name
        self.version = version
        self.files = files
        self.__dict__.update(kwargs)
        self.type = "Total Conversion"


class PredefinedCombination(AutonomousAddon):

    def __init__(self, name, files, **kwargs):
        super(PredefinedCombination, self).__init__()
        self.name = name
        self.files = files
        self.__dict__.update(kwargs)
        self.type = "Predefined Combination"


class Gameplay(ExtendingAddon):

    def __init__(self, name, version, files, **kwargs):
        super(Gameplay, self).__init__()
        self.name = name
        self.version = version
        self.files = files
        self.__dict__.update(kwargs)
        self.type = "Gameplay Mod"


class WeaponPack(ExtendingAddon):

    def __init__(self, name, version, files, **kwargs):
        super(WeaponPack, self).__init__()
        self.name = name
        self.version = version
        self.files = files
        self.__dict__.update(kwargs)
        self.type = "Weapon Pack"


class MapPack(ExtendingAddon):

    def __init__(self, name, version, **kwargs):
        super(MapPack, self).__init__()
        self.name = name
        self.version = version
        self.__dict__.update(kwargs)
        self.type = "Map Pack"


class XimStarWarsMapPack(MapPack):

    def __init__(self, name, version, **kwargs):
        self.name = name
        self.version = version
        super(XimStarWarsMapPack, self).__init__(self.name, self.version)
        self.__dict__.update(kwargs)
        self.type = "Xim Star Wars Map Pack"


if __name__ == "__main__":

    launcher = Launcher()
    launcher.select_addon(launcher.total_conversions, True)
    launcher.select_addon(launcher.predefined_combinations, True)
    launcher.select_addon(launcher.gameplay_mods, False)
    while launcher.allows_more_current_type:
        # TODO: Add list only combinable gameplay mods
        launcher.select_addon(launcher.gameplay_mods, False)
    if not launcher.contains_weapons:
        launcher.select_addon(launcher.weapon_packs, False)
    launcher.select_addon(launcher.allowed_map_packs, True)
