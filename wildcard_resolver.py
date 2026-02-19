import random
import logging
from typing import Optional, List, Dict, Any

try:
    from .random_functions import chance_roll
    from .csv_reader import artist_category_by_category_csv_to_list
except ImportError:
    from random_functions import chance_roll
    from csv_reader import artist_category_by_category_csv_to_list

logger = logging.getLogger(__name__)

class WildcardResolver:
    @staticmethod
    def resolve(completeprompt: str, 
                insanitylevel: int, 
                wildcard: str, 
                listname: List[str], 
                activatehybridorswap: bool, 
                advancedprompting: bool, 
                artiststyleselector: str = "", 
                _metadata: Optional[Dict[str, Any]] = None, 
                metadata_key: Optional[str] = None, 
                list_manager: Optional[Any] = None) -> str:
        
        if len(listname) == 0:
            return completeprompt.replace(wildcard, "", 1)

        while wildcard in completeprompt:
            if chance_roll(insanitylevel, 'unique') and activatehybridorswap and len(listname) > 2 and advancedprompting:
                hybridorswaplist = ["hybrid", "swap"]
                hybridorswap = random.choice(hybridorswaplist)
                
                # Internal pick helper
                def pick_internal(lst, name=None):
                    if list_manager and name:
                        val = list_manager.pick(name)
                    else:
                        val = random.choice(lst)
                    if val in lst:
                        lst.remove(val)
                    return val

                cat_map = {
                    "-artist-": "artists",
                    "-mood-": "moods",
                    "-location-": "locations",
                    "-lighting-": "lighting",
                    "-colorscheme-": "colorscheme"
                }
                cat_name = cat_map.get(wildcard)

                replacementvalue = pick_internal(listname, cat_name)
                
                # Metadata logging for hybrid/swap
                if _metadata is not None and metadata_key is not None:
                    if isinstance(_metadata.get(metadata_key), list):
                        _metadata[metadata_key].append(replacementvalue)
                    else:
                        _metadata[metadata_key] = replacementvalue
                
                hybridorswapreplacementvalue = "[" + replacementvalue
                
                if hybridorswap == "hybrid":
                    replacementvalue = pick_internal(listname, cat_name)
                    if _metadata is not None and metadata_key is not None:
                        if isinstance(_metadata[metadata_key], list):
                            _metadata[metadata_key].append(replacementvalue)
                    hybridorswapreplacementvalue += "|" + replacementvalue + "] "
                
                elif hybridorswap == "swap":
                    replacementvalue = pick_internal(listname, cat_name)
                    if _metadata is not None and metadata_key is not None:
                        if isinstance(_metadata[metadata_key], list):
                            _metadata[metadata_key].append(replacementvalue)
                    hybridorswapreplacementvalue += ":" + replacementvalue + ":" + str(random.randint(1, 20)) + "] "
                
                completeprompt = completeprompt.replace(wildcard, hybridorswapreplacementvalue, 1)

            # Standard selection
            if bool(listname):
                category_map = {
                    "-artist-": "artists",
                    "-mood-": "moods",
                    "-location-": "locations",
                    "-lighting-": "lighting",
                    "-colorscheme-": "colorscheme"
                }
                if list_manager and wildcard in category_map:
                    replacementvalue = list_manager.pick(category_map[wildcard])
                else:
                    replacementvalue = random.choice(listname)
                
                if _metadata is not None and metadata_key is not None:
                    if isinstance(_metadata.get(metadata_key), list):
                        _metadata[metadata_key].append(replacementvalue)
                    else:
                        _metadata[metadata_key] = replacementvalue
                
                if wildcard not in ["-heshe-", "-himher-", "-hisher-"]:
                    if replacementvalue in listname:
                        listname.remove(replacementvalue)
            else:
                replacementvalue = ""

            # Overrides for artists
            if wildcard == "-artist-" and ("-artiststyle-" in completeprompt or "-artistmedium-" in completeprompt or "-artistdescription-" in completeprompt):
                artistscomplete = artist_category_by_category_csv_to_list("artists_and_category", replacementvalue)
                artiststyles = artistscomplete[0]
                artistmediums = artistscomplete[1]
                artistdescriptions = artistscomplete[2]
                
                artiststyle = [x.strip() for x in artiststyles[0].split(",")]
                artiststyle = list(filter(lambda x: len(x) > 0, artiststyle))

                if artiststyleselector in artiststyle:
                    artiststyle.remove(artiststyleselector)
                if "nudity" in artiststyle:
                    artiststyle.remove("nudity")

                while bool(artiststyle) and "-artiststyle-" in completeprompt:
                    chosenartiststyle = random.choice(artiststyle)
                    completeprompt = completeprompt.replace("-artiststyle-", chosenartiststyle, 1)
                    artiststyle.remove(chosenartiststyle)

                if "-artistmedium-" in completeprompt:
                    if artistmediums[0].lower() not in completeprompt.lower():
                        completeprompt = completeprompt.replace("-artistmedium-", artistmediums[0], 1)

                if "-artistdescription-" in completeprompt:
                    completeprompt = completeprompt.replace("-artistdescription-", artistdescriptions[0], 1)
                
                while bool(artiststyle) and "-artiststyle-" in completeprompt:
                    chosenartiststyle = random.choice(artiststyle)
                    completeprompt = completeprompt.replace("-artiststyle-", chosenartiststyle, 1)
                    artiststyle.remove(chosenartiststyle)

            # Sneaky overrides for "same" wildcards
            if wildcard in ["-outfit-", "-minioutfit-"]:
                completeprompt = completeprompt.replace("-sameoutfit-", replacementvalue, 1)

            # Subject reference logic
            if "from" in replacementvalue:
                from_index = replacementvalue.find("from")
                replacementvalueforoverrides = replacementvalue[:from_index].strip()
            else:
                replacementvalueforoverrides = replacementvalue

            # human subject references
            if wildcard in ["-human-", "-humanoid-", "-manwoman-", "-manwomanrelation-", "-manwomanmultiple-"] \
               and "-samehumansubject-" in completeprompt:
                if completeprompt.index(wildcard) < completeprompt.index("-samehumansubject-"):
                    completeprompt = completeprompt.replace("-samehumansubject-", "the " + replacementvalueforoverrides)
            
            if wildcard in ["-fictional-", "-nonfictional-", "-firstname-", "-oppositefictional-", "-oppositenonfictional-"] \
               and "-samehumansubject-" in completeprompt:
                if completeprompt.index(wildcard) < completeprompt.index("-samehumansubject-"):
                    completeprompt = completeprompt.replace("-samehumansubject-", replacementvalueforoverrides)
            
            if wildcard == "-job-" and "-samehumansubject-" in completeprompt:
                if completeprompt.index(wildcard) < completeprompt.index("-samehumansubject-"):
                    completeprompt = completeprompt.replace("-samehumansubject-", "the " + replacementvalueforoverrides)
            
            if wildcard == "-malefemale-" and "-samehumansubject-" in completeprompt:
                if completeprompt.index(wildcard) < completeprompt.index("-samehumansubject-"):
                    completeprompt = completeprompt.replace("-samehumansubject-", "the " + replacementvalueforoverrides)

            if wildcard in ["-animal-", "-object-", "-vehicle-", "-food-", "-objecttotal-", "-space-", "-flora-", "-location-", "-building-"] \
               and "-sameothersubject-" in completeprompt:
                if completeprompt.index(wildcard) < completeprompt.index("-sameothersubject-"):
                    completeprompt = completeprompt.replace("-sameothersubject-", "the " + replacementvalueforoverrides)

            completeprompt = completeprompt.replace(wildcard, replacementvalue, 1)

        return completeprompt
