
SVG_SCHEMA = "http://www.w3.org/Graphics/SVG/1.2/rng/"

DISPOSITIONS = (
    (0, 'Garrison'),
    (1, 'Planetary Defense'), # used
    (2, 'Scout'),     # used
    (3, 'Screen'),    # used
    (4, 'Diplomacy'),
    (5, 'Attack'),    # used
    (6, 'Colonize'),  # used
    (7, 'Patrol'),    # used  
    (8, 'Trade'),     # used
    (9, 'Piracy'),    # used
    )

instrumentalitytypes = [
  {'name': 'Long Range Sensors 1',
   'shortid': 'lrs1',
   'type': 0,
   'description': "Increases the radius over which this planet's sensors " +
                  "can see by .5 G.U.'s.  Does not increase sensor ranges " +
                  "for fleets.",
   'requires': -1,
   'minsociety': 10,
   'upkeep': .01,
   'minupkeep': 100,
   'required':   {'people': 1000, 'food': 1000, 'steel': 150, 
                 'antimatter': 5, 'quatloos': 400, 'hydrocarbon': 500,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Long Range Sensors 2',
   'shortid': 'lrs2',
   'type': 1,
   'description': "Increases the radius over which this planet's sensors " +
                  " can see by another .5 G.U.'s beyond the added range " +
                  "given by Long Range Sensors 1.",
   'requires': 0,
   'minsociety': 20,
   'upkeep': .02,
   'minupkeep': 100,
   'required':   {'people': 1000, 'food': 1000, 'steel': 300, 
                 'antimatter': 10, 'quatloos': 600, 'hydrocarbon': 1000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Trade Incentives',
   'shortid': 'tradeincentives',
   'type': 2,
   'description': "Promotes trade by reducing the price of " +
                  "commodities that are in surplus, and raising the prices of " +
                  "commodities that are needed.  The Government subsidizes the difference " +
                  "in prices through its treasury.",
   'requires': -1,
   'minsociety': 1,
   'upkeep': .01,
   'minupkeep': 50,
   'required':   {'people': 100, 'food': 100, 'steel': 10, 
                 'antimatter': 0, 'quatloos': 100,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Regional Government',
   'shortid': 'rglgvt',
   'type': 3,
   'description': "Allows this planet to collect taxes from it's neighbors.  This tax is " +
                  "fixed at 5%, and please note that if you set all your planets as " +
                  "regional goverments, you're just moving a lot of money around with no " +
                  "advantage.",
   'requires': -1,
   'minsociety': 30,
   'upkeep': .02,
   'minupkeep': 100,
   'required':   {'people': 5000, 'food': 5000, 'steel': 500, 
                 'antimatter': 200, 'quatloos': 10000, 'hydrocarbon': 1000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Mind Control',
   'shortid': 'mindcontrol',
   'type': 4,
   'description': "Every inhabitant of this planet is issued an antenna " +
                  "beanie that turns them into a mindless automaton.  The " + 
                  "consequences of this enbeaniement are that the level of " +
                  "society on the planet does not change.  Naturally this " +
                  "technology is not looked upon favorably by the international " +
                  "community.  Also, certain elements in society resist the wearing " +
                  "of their handsome new headgear, and will have to be...eliminated.",
   'requires': -1,
   'minsociety': 40,
   'upkeep': .2,
   'minupkeep': 100,
   'required':   {'people': 20000, 'food': 500, 'steel': 2000, 
                 'antimatter': 10, 'quatloos': 5000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Matter Synth 1',
   'shortid': 'mattersynth1',
   'type': 5,
   'description': "A matter synthesizer allows you to produce the artificial " +
                  "element *Krellenium*, (Krell Metal), which is used in building " +
                  "military ships beyond the most basic types.  If you wish to build " +
                  "these kinds of ships on this planet you will also need to build a " +
                  "military base.",
   'requires': -1,
   'minsociety': 50,
   'upkeep': .025,
   'minupkeep': 250,
   'required':   {'people': 5000, 'food': 5000, 'steel': 1000, 
                 'antimatter': 500, 'quatloos': 10000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Matter Synth 2',
   'shortid': 'mattersynth2',
   'type': 6,
   'description': "Adds an Unobtanium extractor to the matter synthesizer " +
                  "already located on this planet.  Unobtanium is used in " + 
                  "the production of larger military ships.",
   'requires': 5,
   'minsociety': 70,
   'upkeep': .1,
   'minupkeep': 300,
   'required':   {'people': 5000, 'food': 5000, 'steel': 2000, 
                 'antimatter': 1000, 'quatloos': 20000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Military Base',
   'shortid': 'militarybase',
   'type': 7,
   'description': "A military base, along with a matter synthesizer, allows you " +
                  "to build larger warships on this planet.",
   'requires': 5,
   'minsociety': 60,
   'upkeep': .15,
   'minupkeep': 500,
   'required':   {'people': 2000, 'food': 2000, 'steel': 1000, 
                 'antimatter': 100, 'quatloos': 10000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Slingshot',
   'shortid': 'slingshot',
   'type': 8,
   'description': "A slingshot gives a speed boost to any fleet leaving this planet. ",
                  
   'requires': -1,
   'minsociety': 25,
   'upkeep': .1,
   'minupkeep': 200,
   'required':   {'people': 100, 'food': 100, 'steel': 500, 
                 'antimatter': 10, 'quatloos': 1000,
                 'unobtanium':0, 'krellmetal':0}},
                 
                 
                 ]

shiptypes = {
  'scouts':           {'singular': 'scout', 'plural': 'scouts', 
                       'nice': 'Scouts',
                       'accel': .4, 'att': 1, 'def': 0,'requiresbase':False, 
                       'sense': .5, 'effrange': .5,
                       'upkeep':
                         {'food': 1, 'quatloos': 20},
                       'required':
                         {'people': 5, 'food': 5, 'steel': 10, 
                         'antimatter': 1, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'blackbirds':       {'singular': 'blackbird', 'plural': 'blackbirds', 
                       'nice': 'Blackbirds',
                       'accel': .8, 'att': 0, 'def': 10,'requiresbase':False, 
                       'sense': 1.0, 'effrange': .5,
                       'upkeep':
                         {'food': 1, 'quatloos': 400},
                       'required':
                         {'people': 5, 'food': 5, 'steel': 20, 
                         'antimatter': 5, 'quatloos': 2000,
                         'unobtanium':5, 'krellmetal':10}
                      },
  'arcs':             {'singular': 'arc', 'plural': 'arcs', 'nice': 'Arcs',
                       'accel': .25, 'att': 0, 'def': 1, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'upkeep':
                         {'food': 1, 'quatloos': 30},
                       'required':
                         {'people': 500, 'food': 1000, 'steel': 200, 
                         'antimatter': 10, 'quatloos': 200,
                         'unobtanium':0, 'krellmetal':0}
                      },

  'merchantmen':      {'singular': 'merchantman', 'plural': 'merchantmen', 
                       'nice': 'Merchantmen',
                       'accel': .28, 'att': 0, 'def': 1, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'upkeep':
                         {'food': 4, 'quatloos': -20},
                       'required':
                         {'people': 20, 'food': 20, 'steel': 30, 
                         'antimatter': 2, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'bulkfreighters':   {'singular': 'bulkfreighter', 'plural': 'bulkfreighters', 
                       'nice': 'Bulk Freighters',
                       'accel': .25, 'att': 0, 'def': 1, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'upkeep':
                         {'food': 4, 'quatloos': -30},
                       'required':
                         {'people': 20, 'food': 20, 'steel': 100, 
                         'antimatter': 2, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'fighters':         {'singular': 'fighter', 'plural': 'fighters', 
                       'nice': 'Fighters',
                       'accel': 0.0,
                       'att': 5, 'def': 1, 'requiresbase':True,
                       'sense': 1.0, 'effrange': 2.0,
                       'upkeep':
                         {'quatloos': 2},
                       'required':
                         {'people': 0, 'food': 0, 'steel': 1, 
                         'antimatter': 0, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'frigates':         {'singular': 'frigate', 'plural': 'frigates', 
                       'nice': 'Frigates',
                       'accel': .35, 'att': 10, 'def': 1, 'requiresbase':False,
                       'sense': .4, 'effrange': 1.0,
                       'upkeep':
                         {'food': 10, 'quatloos': 40},
                       'required':
                         {'people': 50, 'food': 50, 'steel': 50, 
                         'antimatter': 10, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'subspacers':       {'singular': 'subspacer', 'plural': 'subspacers', 
                       'nice': 'Sub Spacers',
                       'accel': .3, 'att': 20, 'def': 1, 'requiresbase':False,
                       'sense': .8, 'effrange': 1.0,
                       'upkeep':
                         {'food': 1, 'quatloos': 60},
                       'required':
                         {'people': 50, 'food': 50, 'steel': 50, 
                         'antimatter': 10, 'quatloos': 1000,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'destroyers':       {'singular': 'destroyer', 'plural': 'destroyer', 
                       'nice': 'Destroyers',
                       'accel':.32, 'att': 70, 'def': 3, 'requiresbase':False,
                       'sense': .5, 'effrange': 1.2,
                       'upkeep':
                         {'food': 12, 'quatloos': 50},
                       'required':
                         {
                         'people': 60, 'food': 70, 'steel': 100, 
                         'antimatter': 12, 'quatloos': 400,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'cruisers':         {'singular': 'cruiser', 'plural': 'cruisers', 
                       'nice': 'Cruisers',
                       'accel': .32, 'att': 150, 'def': 6, 'requiresbase':True,
                       'sense': .7, 'effrange': 1.8,
                       'upkeep':
                         {'food': 16, 'quatloos': 60},
                       'required':
                         {
                         'people': 80, 'food': 100, 'steel': 200, 
                         'antimatter': 20, 'quatloos': 1200,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'battleships':      {'singular': 'battleship', 'plural': 'battleships', 
                       'nice': 'Battleships',
                       'accel': .25, 'att': 320, 'def': 12, 'requiresbase':True,
                       'sense': .7, 'effrange': 2.0,
                       'upkeep':
                         {'food': 21, 'quatloos': 80},
                       'required':
                         {
                         'people': 110, 'food': 200, 'steel': 1000, 
                         'antimatter': 50, 'quatloos': 4000,
                         'unobtanium':0, 'krellmetal':10}
                      },
  'superbattleships': {'singular': 'super battleship', 'plural': 'super battleships', 
                       'nice': 'Super Battleships',
                       'accel': .24, 'att': 500, 'def': 15, 'requiresbase':True,
                       'sense': 1.0, 'effrange': 2.0,
                       'upkeep':
                         {'food': 30, 'quatloos': 100},
                       'required':
                         {
                         'people': 150, 'food': 300, 'steel': 5000, 
                         'antimatter': 150, 'quatloos': 8000,
                         'unobtanium':10, 'krellmetal':20}
                      },
  'carriers':         {'singular': 'carrier', 'plural': 'carriers', 
                       'nice': 'Carriers',
                       'accel': .2, 'att': 0, 'def': 10, 'requiresbase':True,
                       'sense': 1.2, 'effrange': .5,
                       'upkeep':
                         {'food': 100, 'quatloos': 200},
                       'required':
                         {
                         'people': 500, 'food': 500, 'steel': 7500, 
                         'antimatter': 180, 'quatloos': 10000,
                         'unobtanium':35, 'krellmetal':50} 
                       }
  }
productionrates = {'people':        {'baseprice': 100, 'pricemod':.003, 'nice': 'People', 
                                     'baserate': 1.12, 'socmodifier': -0.00002, 'neededupgrade': -1,
                                     'initial': 150000},
                   'quatloos':      {'baseprice': 1, 'pricemod':1.0,  'nice': 'Quatloos',
                                     'baserate': 1.0, 'socmodifier': 0.0, 'neededupgrade': -1,

                                     'initial': 1000},
                   'food':          {'baseprice': 10, 'pricemod':-.00002,  'nice': 'Food',
                                     'baserate': 1.09, 'socmodifier': -.00108, 'neededupgrade': -1,

                                     'initial': 5000},
                   'consumergoods': {'baseprice': 30, 'pricemod':.02,  'nice': 'Consumer Goods',
                                     'baserate': .9999, 'socmodifier': .0000045, 'neededupgrade': -1,

                                     'initial': 2000},
                   'steel':         {'baseprice': 100, 'pricemod':-.05,  'nice': 'Steel',
                                     'baserate': 1.001, 'socmodifier': 0.0, 'neededupgrade': -1,

                                     'initial': 500},
                   'unobtanium':    {'baseprice': 20000, 'pricemod':10000.0, 'nice': 'Unobtanium',
                                     'baserate': .99999, 'socmodifier': .00000035, 
                                     'neededupgrade': 6, #Instrumentality.MATTERSYNTH2
                                     'initial': 0},
                   'krellmetal':    {'baseprice': 10000, 'pricemod':100.0,  'nice': 'Krell Metal',
                                     'baserate': .999995, 'socmodifier':.0000008, 
                                     'neededupgrade': 5, #Instrumentality.MATTERSYNTH1
                                     'initial': 0},
                   'antimatter':    {'baseprice': 5000, 'pricemod':4.0,  'nice': 'Antimatter',
                                     'baserate': .9999, 'socmodifier': .000008, 'neededupgrade': -1,
                                     'initial': 50},
                   'hydrocarbon':   {'baseprice': 100, 'pricemod':-.009,  'nice': 'Hydrocarbon',
                                     'baserate': 1.013, 'socmodifier': -.00014, 'neededupgrade': -1,

                                     'initial': 1000}
                  }
