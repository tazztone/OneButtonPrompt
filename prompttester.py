import sys, os
import random
import uuid
import re
from superprompter.superprompter import *
from datetime import datetime
sys.path.append(os.path.abspath(".."))


from build_dynamic_prompt import *



def generateprompts(amount = 1,insanitylevel="5",subject="all", artist="all", imagetype="all",onlyartists=False, workprompt="", antistring="",prefixprompt="", suffixprompt="", negativeprompt="",promptcompounderlevel = "1", seperator="comma",givensubject="",smartsubject=True,giventypeofimage="",imagemodechance=20, gender = "all", subtypeobject = "all", subtypehumanoid = "all", subtypeconcept = "all", advancedprompting = True, hardturnoffemojis=False, seed=0, overrideoutfit="", prompt_g_and_l = False, base_model = "SD1.5", OBP_preset = "", prompt_enhancer="none", preset_prefix = "", preset_suffix =""):
    from prompt_config import PromptConfig
    from prompt_engine import PromptEngine

    # Build config from arguments
    # Filter out non-config args like 'amount' which is local to this function
    cfg = PromptConfig.from_kwargs(**{k: v for k, v in locals().items() if k != "amount"})

    loops = int(amount)  # amount of images to generate
    steps = 0
   
    insanitylevel = int(insanitylevel)
    while steps < loops:
        # build prompt
        if(prompt_g_and_l == True):
            resultlist = PromptEngine.generate(cfg)
            result = resultlist[0]
            print("prompt_g")
            print(resultlist[1])
            print("prompt_l")
            print(resultlist[2])

        else:
            configs = cfg
            # If we need to override anything specifically for the loop, we can
            # but here it seems static per call
            result = PromptEngine.generate(configs)[0]

        #if(superprompter):
        #    load_models()
        #    superpromptresult1 = answer(input_text=result, max_new_tokens=150, repetition_penalty=1.5, temperature=0.5, top_p=0.1, top_k=10, seed=seed)
        #    superpromptresult2 = answer(input_text="Help me prompt this a little bit better and concise: """ + result + "" , max_new_tokens=150, repetition_penalty=1.5, temperature=0.5, top_p=0.1, top_k=10, seed=seed)
        #    superpromptresult3 = answer(input_text="Make this more artful: """ + result + "" , max_new_tokens=150, repetition_penalty=1.5, temperature=5.0, top_p=5, top_k=1, seed=seed)
        #    superpromptresult4 = answer(input_text="Describe this for me please: """ + result + "" , max_new_tokens=150, repetition_penalty=1.5, temperature=5.0, top_p=5, top_k=1, seed=seed)
        # unload_models()

            #print (result + " --- " + superpromptresult1 + " --- " + superpromptresult2 + " --- " + superpromptresult3  + " --- " + superpromptresult4)

        print("")
        print("loop " + str(steps))
        print("")
        if(onlyartists == True):
            print(result)
            print("")
        
        if(result.count("-")>1 and imagetype == "only templates"):
            print("Is there a mistake in wildcards?")
            print("")
            print(result)
            break
            
        if(givensubject != "" and givensubject not in result and imagetype == "only templates"):
            print("No givensubject, there must be an issue:")
            print("")
            print(result)
            break

        if(overrideoutfit != "" and overrideoutfit not in result and onlyartists == False and "-outfit-" not in overrideoutfit):
            print("The outfit override is not showing up!")
            print("")
            print(result)
            break

        if(" OR " in result or ";" in result):
            print("There is a mistake in a OR statement")
            print("")
            print(result)
            break
        
        # Use regex to find words enclosed by hyphens, the wildcards1
        # make some minor exceptions
        resultnew = result
        resultnew = resultnew.replace("-eye-", " eye ")
        resultnew = resultnew.replace("-of-", " of ")
        resultnew = resultnew.replace("-the-", " the ")
        resultnew = resultnew.replace("-up-", " up ")
        resultnew = resultnew.replace("-in-", " in ")
        resultnew = resultnew.replace("-au-", " au ")
        resultnew = resultnew.replace("-da-", " da ")
        resultnew = resultnew.replace("-doo-", " doo ")
        resultnew = resultnew.replace("-and-", " and ")
        resultnew = resultnew.replace("-o-", " o ")
        resultnew = resultnew.replace("-horse-", " horse ")
        matches = re.findall(r'-\w+-', resultnew)

        # Filter out matches with commas and spaces
        wildcards = [match for match in matches if ',' not in match and ' ' not in match]
        

        if(wildcards):
            print("There is a wildcard still in the prompt")
            print("")
            print(result)
            break

        #if("game" in result or "movie" in result or "series" in result):
        #    print("TEST THIS")
        #    print("")
         #   print(result)
        #    break

        steps += 1
    

    print("")
    print("All done!")

if __name__ == "__main__":
    generateprompts(
        amount=10,
        insanitylevel=5,
        subject="all",
        artist="all",
        imagetype="all",  # "only other types", "only templates mode", etc.
        onlyartists=False,
        antistring="",
        prefixprompt="",
        suffixprompt="",
        negativeprompt="",
        promptcompounderlevel=1,
        seperator="",
        givensubject="",
        smartsubject=True,
        giventypeofimage="",
        imagemodechance=5,
        gender="all",
        subtypeobject="all",
        subtypehumanoid="all",
        subtypeconcept="all",
        advancedprompting=False,
        hardturnoffemojis=True,
        seed=-1,
        overrideoutfit="",
        prompt_g_and_l=False,
        base_model="SDXL",
        OBP_preset="",
        prompt_enhancer="",
        preset_prefix="hello",
        preset_suffix="",
    )