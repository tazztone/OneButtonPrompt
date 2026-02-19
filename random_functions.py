import random
import logging

# Set up logger
logger = logging.getLogger(__name__)

# CHANCE_MAPPING mapping moved to here as it is only used by chance_roll function.
# ... (CHANCE_MAPPING content)
CHANCE_MAPPING = {
    'never': {'set_number': 0, 'message': ""},
    'novel': {'set_number': 500, 'message': "Uh, something novel has been added to the prompt. Interesting."},
    'extraordinary': {'set_number': 200, 'message': "Extraordinary! Something special has been added to the prompt"},
    'unique': {'set_number': 75, 'message': "Critical hit! Something unique has been added to the prompt"},
    'legendary': {'set_number': 50, 'message': "Nice! adding something legendary to the prompt"},
    'rare': {'set_number': 30, 'message': "adding something rare to the prompt"},
    'uncommon': {'set_number': 18, 'message': ""},
    'normal': {'set_number': 10, 'message': ""},
    'common': {'set_number': 5, 'message': ""},
    'always': {'set_number': 1, 'message': ""},
}

def chance_roll(insanitylevel, chance):
    if chance == 'always':
        return True
    if chance == 'never':
        return False
    if chance in CHANCE_MAPPING:
        properties = CHANCE_MAPPING[chance]
        set_number = properties['set_number']
        message = properties['message']
        # if we have insanity level of 10, then every under rare is alwas true
        if (set_number <= 35 and insanitylevel >= 10):
            if(message != ""):
                logger.debug(message)
            return True 
        roll = random.randint(1, set_number) <= insanitylevel
        if(message != "" and roll == True):
            logger.debug(message)
        return roll
    else:
        raise ValueError(f"Invalid chance value: {chance}")
