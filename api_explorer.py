#GET /api/spells
#curl -X GET "https://www.dnd5eapi.co/api/ability-scores/cha" -H "Accept: application/json"
import json
from tqdm.auto import tqdm
import os
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd

cmap = plt.get_cmap('viridis')

#======RUN THIS TO DOWNLOAD SPELL DATA THAT IS USED LATER
"""# Opening JSON file
f = open('spells.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
print(data['results'])
# Closing file
f.close()

for d in tqdm(data['results']):
    spell_name = d['index']
    url = d['index']
    os.system(f'curl -X GET "https://www.dnd5eapi.co/api/spells/{url}" -H "Accept: application/json" --output spells/{spell_name}.json')"""

spell = "fireball"
spells_dir = "spells/"
f = open(f"{spells_dir}{spell}.json")
data = json.load(f)
f.close()



def decode_damage(damage_json):
    damage_array = np.zeros((10))
    for i in damage_json.keys():
        damage_str = damage_json[i]
        if "+" in damage_str:
            m = damage_str.split("+")[-1]
            n,s = damage_str.split("+")[0].split("d")
        elif "-" in damage_str:
            m = damage_str.split("-")[-1]
            n,s = damage_str.split("-")[0].split("d")
        else:
            m = 0
            try:
                n,s = damage_str.split("d")
            except:
                print(damage_str)
        try:
            n,s,m = int(n),int(s),int(m)
        except:
            print(f"Error in damage decoding {damage_json}")
            return([np.nan]*10)
        damage_array[int(i)] = mean_damage(n,s,m)
    damage_array[damage_array == 0] = np.nan
    return(damage_array)

def decode_spell(spell_name,spells_dir = "spells/"):
    f = open(f"{spells_dir}{spell_name}.json")
    data = json.load(f)
    #print(data.keys())
    f.close()
    
    school = data['school']['name']
    spell_range = data['range']
    if "dc" in data.keys():
        DC = data['dc']['dc_type']['name']
    else:
        DC = None
    if 'damage' in data.keys():
        try:
            dtype = data['damage']['damage_type']['name']
        except:
            dtype = None
        if "damage_at_slot_level" in data['damage'].keys():

            damage_json = data['damage']['damage_at_slot_level']
            damage_array = decode_damage(damage_json)
        else:
            damage_array = [np.nan]*10
        
    else:
        dtype = None
        damage_array = [np.nan]*10
    
    return(dtype,school,spell_range,DC,damage_array)

def read_spell_json(spell_name,spells_dir = "spells/",
                    search = ["damage","dtype","dc","ritual","concentration","duration","casting_time","level","school","classes","components","AoE","range"]):
    
    out = []
    out_labels = []
    f = open(f'{spells_dir}{spell_name}.json')
    data = json.load(f)

    keys = data.keys()
    #print("=====================\n",keys,"\n=========================")
    #=============Get Damage=============
    #create empty damage list, no damage gets nan values (i.e. it is not 0 damage it is no damage)
    damage = [np.nan]*10

    try:
        if "damage" in keys and "dtype" in search:

            dtype = data['damage']['damage_type']['name']
            out.append(dtype)
            out_labels.append("damage_type")
        else:
            if "dtype" in search:
                out.append(None)
                out_labels.append("dtype")
    except Exception as e:
        print("WARNING ERROR IN DTYPE=========\n",e,"\n=================")
        if "dtype" in search:
            dtype = None
            out.append(dtype)

    if "damage" in keys and "damage" in search:
        
        if "damage_at_slot_level" in data['damage'].keys():
            damage_json = data['damage']['damage_at_slot_level']
            for i in damage_json.keys():
                dice_count = damage_json[i].count("d")
                if  dice_count == 1:
                    damage[int(i)] = damage_dice(damage_json[i])
                elif dice_count == 0:
                    damage[int(i)] = damage_json[i] 
                else:
                    damage[int(i)] = [damage_dice(dj) for dj in damage_json[i].split(" + ")]
        out.append(damage)
        out_labels.append("damage")
    else:
        if "damage" in search: out.append(damage)

    #=============DC========
    if "dc" in data.keys() and "dc" in search:
        dc_type = data['dc']['dc_type']['name']
    elif "dc" not in data.keys() and "dc" in search:
        dc_type = None
        out.append(dc_type)
        out_labels.append("DC")

    if "ritual" in search: 
        ritual = bool(data['ritual'])
        out.append(ritual)
        out_labels.append("ritual")
    if "concentration" in search:
        concentration = bool(data['concentration'])
        out.append(concentration)
        out_labels.append("concentration")

    if "duration" in search:
        duration = data['duration']
        out.append(duration)
        out_labels.append("duration")

    if "casting_time" in search:
        casting_time = data['casting_time']
        out.append(casting_time)
        out_labels.append("casting_time")

    if "level" in search:
        level = int(data['level'])
        out.append(level)
        out_labels.append("level")
    
    if "school" in search:
        school = data['school']['name']
        out.append(school)
        out_labels.append("school")
    


    #==========================
    if "classes" in search:
        class_list = []
        for classes in data['classes']:
            class_list.append(classes['name'])
        out.append(class_list)
        out_labels.append("class_list")
        
        
    if "area_of_effect" in keys and "AoE" in search:
        AoE = data['area_of_effect']
        out.append(AoE)
        out_labels.append("AoE")
    elif "AoE" in search:
        out.append(None)
        out_labels.append("AoE")

    #========Components======
    if "components" in search:
        components = data['components']
        #out.append(components)
        V,S,M = False,False,False
        if "V" in components: V = True
        if "S" in components: S = True
        if "M" in components: M = True
        out.append([V,S,M])
        out_labels.append("Components")
    

    if "range" in search:
        spell_range = data['range']
        out.append(spell_range)
        out_labels.append("Range")
    
    return(out,out_labels)

def AoE_parser(aoe_in):
    if aoe_in == None:
        return("None")
    else:
        
        return(f"{aoe_in['type']} ({aoe_in['size']})")
    
def none_parser(input_str):
    if input_str == None:
        return("None")
    else:
        return(input_str)
    
def spell_survey(spells_dir = "spells/"):
    D,L,S,A,R = [],[],[],[],[]
    for spell in tqdm(os.listdir(spells_dir)):
        #print(spell.replace(".json","").replace("-"," "))
        [dtype,level,school,AoE,range],_ = read_spell_json(spell.replace(".json",""),search = ["dtype","level","school","AoE","range"])
        """print("dtype: ",dtype)
        print("level: ",level)
        print("school: ",school)
        print("AoE: ",AoE)
        print("range: ",range)"""
        D.append(none_parser(dtype))
        L.append(none_parser(level))
        S.append(none_parser(school))
        A.append(AoE_parser(AoE))
        R.append(none_parser(range))
    #print(D)
    #print(L)
    #print(S)
    #print(A)
    #print(R)
    D_set = sorted(list(set(D)))
    L_set = sorted(list(set(L)))
    S_set = sorted(list(set(S)))
    A_set = sorted(list(set(A)))
    R_set = sorted(list(set(R)))
    return(D_set,L_set,S_set,A_set,R_set)

class damage_dice():
    def __init__(self,damage_str):
        super().__init__()
        values = damage_str.split("d")
        if "+" in damage_str:
            m = damage_str.split("+")[-1]
            n,s = damage_str.split("+")[0].split("d")
        elif "-" in damage_str:
            m = damage_str.split("-")[-1]
            n,s = damage_str.split("-")[0].split("d")
        else:
            m = 0
            try:
                n,s = damage_str.split("d")
            except Exception as e:

                print(damage_str)
                raise(e)
        try:
            self.n,self.s,self.m = int(n),int(s),int(m)
        except Exception as e:
            raise(e)
    def mean_damage(self):
        av = ( (self.s + 1 )/ 2 ) * self.n + self.m 
        return(av)
        
def spell_saying_guide(spell):
    [dtype,level,school,AoE,range],_ = read_spell_json(spell.replace(".json",""),search = ["dtype","level","school","AoE","range"])
    data = pd.read_excel("Spell_Saying_Guide.xlsx")
    dtype = none_parser(dtype)
    level = none_parser(level)
    school = none_parser(school)
    AoE = AoE_parser(AoE)
    range = none_parser(range)

    
    damage_sound = str(data['sound_dtype'][list(data['dtype']).index(dtype)])
    level_sound = str(data['sound_level'][list(data['level']).index(level)])
    school_sound = str(data['sound_school'][list(data['school']).index(school)])
    aoe_sound = str(data['sound_aoe'][list(data['aoe']).index(AoE)])
    range_sound = str(data['sound_range'][list(data['range']).index(range)])

    sounds = [level_sound.capitalize(),
              school_sound.lower(),
              damage_sound.lower(),
              aoe_sound.capitalize(),
              range_sound.lower()]
    return("".join(sounds[:3]).replace("Dash","'") +"-" +  "".join(sounds[3:]).replace("Dash","'"))

def make_spell_language_guide(spells_dir = "spells/"):
    Letter = ""
    final_text = ""
    for spell in os.listdir(spells_dir):
        if spell[0].capitalize() != Letter: 
            Letter = spell[0].capitalize()
            final_text += "\subsection{" + Letter +"}\n"
        said = spell_saying_guide(spell.replace(".json",""))
        final_text += '\entry{' + " ".join([s.capitalize() for s in spell.replace(".json","").replace("-"," ").split(" ")] )+ "}{" + said + r"} \\" + "\n"
    print(final_text)
"""f = open('spells.json')
data = json.load(f)
f.close()
L = data['count']
spell_slots = range(10)
for i,d in enumerate(data['results']):
    spell_name = d['index']
    _,_,_,_,damage_array = decode_spell(spell_name)
    plt.plot(spell_slots,damage_array,c = cmap(i/L))
plt.xlabel("Spell Slot")
plt.xticks(range(10),range(10))
plt.ylabel("Average Damage")
plt.savefig("figures/damagevsslot")
plt.clf()"""

"""#Get the spell keys for guides
D_set,L_set,S_set,A_set,R_set =spell_survey()
print("------Damage Types------")
for d in D_set:
    print(d)
print("-------Level----------")
for l in L_set:
    print(l)
print("------School-------")
for s in S_set:
    print(s)
print("-------Area of Effect------")
for a in A_set:
    print(a)
print("--------Range-----")
for r in R_set:
    print(r)
    """


#print(data['Sound_1'][list(data['Damage Type']).index("None")])

#make_spell_language_guide()