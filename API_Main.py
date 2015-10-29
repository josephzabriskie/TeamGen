from pprint import pprint
import sys
from time import sleep
from requests import get


class api_commands:  # this class contains all api calls as functions
    def __init__(self):
        self.command_cnt = 0
        self.apikey = 'api_key=53731de1-b974-4841-b412-d363ce9db46e'
        self.cps = 1.0  # Calls per Second
        self.baseurl = 'https://na.api.pvp.net/api/lol/na/'
        self.section_verison = {'summoner': 'v1.4/summoner/',
                                'team': 'v2.4/team/',
                                'stats': 'v1.3/stats/',
                                'matchlist': 'v2.2/matchlist/',
                                'matchhistory': 'v2.2/matchhistory/',
                                'match': 'v2.2/match/',
                                'league': 'v2.5/league/'}
        self.RateLimitOk = True
        self.debug = False

    def url_build_exec_verify(self, arguments, section, optional_args='', prefix='', suffix=''):
        if not prefix == '':
            if prefix.startswith('/'):
                prefix = prefix[1:len(prefix)]
            if not prefix.endswith('/'):
                prefix += '/'
        if not suffix == '':  # TODO check this fix for suffixes, kinda messy
            if not suffix.endswith('?'):
                suffix += '?'
            if not suffix.startswith('/'):
                suffix = '/' + suffix
            if arguments.endswith('?'):
                arguments = arguments[:-1]
        myurl = self.baseurl + self.section_verison[section] + prefix + arguments + optional_args + suffix + self.apikey
        if self.debug:
            print('url {}'.format(myurl))

        def restart_line():
            sys.stdout.write('\r')
            sys.stdout.flush()

        timeout = 20
        while timeout > 0:
            output = get(myurl)
            if self.check_status_code(output.status_code):
                rslt = output.json()
                return rslt
            else:
                if timeout == 20:
                    sys.stdout.write('Retrying...(0)')
                else:
                    restart_line()
                    sys.stdout.write('Retrying...({})'.format(20-timeout))
                sleep(self.cps)
                timeout -= 1
        print('{} Tries elapsed, for url: {}'.format(20, myurl))

    def check_status_code(self, code):
        if code == 200:
            return True
        elif code == 404:
            print('No information for api')
        else:
            if code == 429:
                self.RateLimitOk = False
            return False

    def build_args(self, args, optional_args=None):  # todo make optional args
        retstr = ''
        if isinstance(args, list):
            for elem in args:
                retstr += str(elem) + ','
            retstr = retstr[:-1]
            retstr += '?'
        else:
            retstr += str(args) + '?'
        if isinstance(optional_args, dict) and len(optional_args) > 0:
            for key in optional_args:
                if not isinstance(optional_args[key], list):
                    retstr += key + '=' + str(optional_args[key]) + '&'
                else:
                    retstr += key + '=' + (','.join(optional_args[key])) + '&'  # TODO remove spaces and lowercase all letters
        if self.debug:
            print('retstr = {}'.format(retstr))
        return retstr

# Summoner Parsing Functions--------------------------------------------------------------
    def parse_summoner_info(self, desiredvalues, summonerinfo):
        outdict = {}
        if isinstance(desiredvalues, list):
            for val in desiredvalues:
                outdict.update(val, summonerinfo.get(val, 'input error'))
            return outdict
        else:
            outdict.update(desiredvalues, summonerinfo.get(desiredvalues, 'input error'))
            return outdict

# Summoner API Calls--------------------------------------------------------------todo limit of 10 on multiple summoner ids
    def summoner_info_byname(self, names):
        args = self.build_args(names)
        rslt = self.url_build_exec_verify(args, 'summoner', prefix='by-name')
        return rslt

    def summoner_info_byID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'summoner')
        return rslt

    def summoner_masteries_byID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'summoner', suffix='masteries')
        return rslt

    def summoner_name_byID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'summoner', suffix='name')
        return rslt

    def summoner_runes_byID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'summoner', suffix='runes')
        return rslt

# Team API Calls-----------------------------------------------------------------
    def team_by_summonerID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'team', prefix='by-summoner')
        return rslt

    def team_by_teamID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'team')
        return rslt

# Stats API Calls----------------------------------------------------------------
    def stats_summary_byID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'stats',prefix='by-summoner', suffix='summary')
        return rslt

    def stats_ranked_byID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'stats',prefix='by-summoner', suffix='ranked')
        return rslt

# Matchlist API Calls------------------------------------------------------------
    def match_list_byID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'matchlist',prefix='by-summoner')
        return rslt

# MatchHistory API Calls---------------------------------------------------------
    def match_history_byID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'matchhistory')
        return rslt

# Match API Call------------------------------------------------------------------
    def match_by_matchID(self, idnum):
        args = self.build_args(idnum)
        rslt = self.url_build_exec_verify(args, 'match')
        return rslt

# Match Info API Calls------------------------------------------------------------

# Leagues Info API Calls----------------------------------------------------------
    def league_entry_byID(self, idnums):
        args = self.build_args(idnums)
        rslt = self.url_build_exec_verify(args, 'league', prefix='by-summoner', suffix='entry')
        return rslt

if __name__ == '__main__':
    print('hello, doing work')
    com = api_commands()
    myname = ['MillionYearRain', 'Mudwater']
    name = 'FantasticMrFaux'
    myids = [26092342, 23511833]
    myid = 26092342
    matchid = 1620408364
    teamids = 'TEAM-8f051670-321a-11e2-9805-782bcb4d1861'
    names10 = [45453153, 46300504, 26426955, 5908, 23511833, 39851168, 26472631, 24207261, 39891271, 60481297]
    output = com.league_entry_byID(names10)
    try:
        pprint(output)
    except:
        pprint(str(output).encode('utf-8'))
