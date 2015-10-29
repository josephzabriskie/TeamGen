from API_Main import api_commands
import random
from pprint import pprint

scorekeylist = ["B5", "B4", "B3", "B2", "B1", "S5", "S4", "S3", "S2", "S1", "G5", "G4", "G3", "G2", "G1", "P5", "P4", "P3",
         "P2", "P1", "D5", "D4", "D3", "D2", "D1", "A"]

scores = {"B5": 1.0, "B4": 1.045, "B3": 1.094, "B2": 1.154, "B1": 1.22, "S5": 1.284, "S4": 1.446, "S3": 1.578,
          "S2": 1.725, "S1": 1.861, "G5": 1.944, "G4": 2.113, "G3": 2.199, "G2": 2.286, "G1": 2.323, "P5": 2.421,
          "P4": 2.509, "P3": 2.557, "P2": 2.599, "P1": 2.633, "D5": 2.651, "D4": 2.694, "D3": 2.705, "D2": 2.71,
          "D1": 2.713, "A1": 2.716}

tierdict = {'BRONZE': 'B', 'SILVER': 'S', 'GOLD': 'G', 'PLATINUM': 'P', 'DIAMOND': 'D', 'CHALLENGER': 'A', 'MASTER': 'A'}
divisiondict = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}


def retrieve_rank_dict(namelist):
    badnames = []
    api = api_commands()
    nametemp = []
    iddict = {}
    rankdict= {}
    for name in namelist:  #todo this sucks
        nametemp.append(name)
        if len(nametemp) >= 10:
            info = api.summoner_info_byname(nametemp)
            for player in nametemp:
                player = (player.lower()).replace(' ', '')
                try:
                    iddict[player] = info[player]['id']
                except KeyError:
                    badnames.append(player)
            nametemp.clear()
    info = api.summoner_info_byname(nametemp)
    for player in nametemp:
        player = (player.lower()).replace(' ', '')
        iddict[player] = info[player]['id']
    templist = []
    print('BadNames: {}'.format(badnames))
    for key in sorted(iddict):
        templist.append(iddict[key])
        if len(templist) == 10:
            ranks = api.league_entry_byID(templist)
            for idnum in templist:
                if str(idnum) not in ranks:
                    basicinfo = api.summoner_info_byID(idnum)
                    rankdict[basicinfo[str(idnum)]['name']] = ['unranked', 'unranked', basicinfo[str(idnum)]['summonerLevel']]
                else:
                    for entry in ranks[str(idnum)]:
                        if entry['queue'] == 'RANKED_SOLO_5x5':
                            rankdict[entry['entries'][0]['playerOrTeamName']] =\
                                [entry['tier'], entry['entries'][0]['division'], entry['entries'][0]['leaguePoints']]
            templist.clear()
    ranks = api.league_entry_byID(templist)
    for idnum in templist:
        if str(idnum) not in ranks:
            basicinfo = api.summoner_info_byID(idnum)
            rankdict[basicinfo[str(idnum)]['name']] = ['unranked', 'unranked', basicinfo[str(idnum)]['summonerLevel']]
        else:
            for entry in ranks[str(idnum)]:
                if entry['queue'] == 'RANKED_SOLO_5x5':
                    rankdict[entry['entries'][0]['playerOrTeamName']] =\
                        [entry['tier'], entry['entries'][0]['division'], entry['entries'][0]['leaguePoints']]
    return rankdict

def calculate_adjusted_rank(rank_dict):
    outdict = {}
    for player in rank_dict:
        if rank_dict[player][0] == 'unranked':
            outdict[player] = ['UR1', ]
            if rank_dict[player][2] == 30:
                outdict[player].append(1.5)  # TODO this is arbitrary
            else:
                outdict[player].append(0.033*rank_dict[player][2])  # todo this is also not that good
        else:
            outdict[player] = [str(tierdict[rank_dict[player][0]]) + str(divisiondict[rank_dict[player][1]]), ]
            outdict[player].append(scores[outdict[player][0]])
    for player in outdict:
        if outdict[player][0] == 'UR1':
            pass  # make no addition
        elif outdict[player][1] < 101 and outdict[player][0] != 'A1':
            index = scorekeylist.index(outdict[player][0])
            addition = (scores[scorekeylist[index + 1]] - scores[scorekeylist[index]])*float(rank_dict[player][2]/100)
            #print('{} addition: {}'.format(player, addition))
            outdict[player][1] += addition
    return outdict

def make_teams(finaldict):
    def chunks(l, n):
        for j in range(0, len(l), n):
            yield l[j:j+n]

    length = len(finaldict)
    excludedlist = []
    for i in range(length % 5):
        exclude = random.choice(list(finaldict))
        finaldict.pop(exclude)
        excludedlist.append(exclude)
    print('Randomly excluded players: {}'.format(excludedlist))

    sum = 0
    for player in finaldict:
        sum += finaldict[player][1]
    avg = sum/len(finaldict)
    print('average: {}'.format(round(avg, 3)))

    orderedplayers = []
    orderedscores = []
    for player in finaldict:
        if len(orderedplayers) == 0:
            orderedplayers.append(player)
            orderedscores.append(finaldict[player][1])
        else:
            added = False
            for x in range(len(orderedplayers)):
                if finaldict[player][1] > orderedscores[x]:
                    orderedplayers.insert(x, player)
                    orderedscores.insert(x, finaldict[player][1])
                    added = True
                    break
            if not added:
                orderedplayers.append(player)
                orderedscores.append(finaldict[player][1])
    #print('Ordered Players: {}'.format(orderedplayers))
    #print('Ordered Scores: {}'.format(orderedscores))

    section_list = list(chunks(orderedplayers, int(len(finaldict)/5)))
    #print('Player sections')
    #pprint(section_list)
    teamlist = []
    for teamnum in range(len(section_list[0])):
        teamlist.append([])
        for section in section_list:
            name = random.choice(section)
            section.remove(name)
            teamlist[teamnum].append(name)

    #pprint(teamlist)
    for team in teamlist:
        sum = 0
        for teammember in team:
            sum += finaldict[teammember][1]
        avg = round(sum/5, 3)
        print('Team {}. Avg {}'.format(team, avg))
    return teamlist


f = open('Players', 'r')
names = [x.strip('\n') for x in f.readlines()]
print('Names: {}'.format(names))
rank_dict = retrieve_rank_dict(names)
outdict = calculate_adjusted_rank(rank_dict)
teamlist = make_teams(outdict)


























