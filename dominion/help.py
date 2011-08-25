from newdominion.dominion.constants import *




subspacers_info = \
"""
<h1>Sub Spacers</h1>

<p>Sub spacers are small hard to see ships good for commerce raiding
and spying.  Normal ships can be seen if they are inside the sensor range of
another fleet/star; sub spacers can only be seen given a random 
chance dependent on how close they are to the other fleet/star.</p>
 
<p>They lose most of their value if mixed with other ships.</p>
"""

scouts_info = \
"""
<h1>Scouts</h1>

<p>Scouts are fast, and lightly armed.  ideal for watching over trade 
routes, or keeping tabs on your neighbors.</p>

<p>If faced with a real fight, scouts are quickly destroyed.</p>
"""

blackbirds_info  = \
"""
<h1>Blackbirds</h1>
<p>A faster, tougher, more expensive scout. 
Useful for doing reconnaissance over hostile territory.  They also have
the best sensor range of any ship type.</p>

<p>They are very expensive to build, and require a lot of upkeep.</p>
"""


arcs_info    = \
"""
<h1>Arcs (Colony Ships)</h1>

<p>Large ships, used to colonize another star system.  Upon arrival 
at a star system, the colonists will convert the arc into the materials 
needed to start a colony.</p>

<p>While enroute, the colonists are kept in freezers, so maintenance costs
are kept low.</p>
"""

merchantmen_info  = \
"""
<h1>Merchants</h1>
<p>Merchant ships travel from star to star, buying and selling goods
in an attempt to make a profit</p>

<p>Trade happens automatically.  When a merchant fleet arrives at a 
star system, the following happens:</p>
<ol>
  <li>All ships sell the contents of their holds</li>
  <li>Commodity prices are compared against nearby stars</li>
  <li>The fleet chooses the most profitable next destination</li>
  <li>Most profitable commodity is bought, given the amount of money on hand</li>
  <li>Fleet leaves for the next destination</li>
</ol>

<p>Once a certain level of profit is reached, they return to their home 
port and render a profit to their owners (and taxes to the planetary 
government).</p>
"""

bulkfreighters_info  = \
"""
<h1>Bulk Freighters</h1>

<p>Similar to merchantmen, except that they can carry twice as much.</p>

<p>Also, Bulk Freighters tend to return to their home port more often, 
and try to bring back food when they do.  Very useful for star systems that are 
running out of food.</p>
"""

fighters_info     = \
"""
<h1>Fighters</h1>
<p>are small unpiloted drones incapable of interstellar travel.
They can be used as a cheap planetary defense, and can be carried between
stars by a Carrier.</p>

<p>If attacked, the fighters will deploy from the Carrier, and fight alongside
the rest of the fleet.</p>
"""

frigates_info     = \
"""
<h1>Frigates</h1>

<p>The smallest effective military unit.  Designed for use
as convoy escorts, and as a screen for larger military units.</p>
"""

destroyers_info   = \
"""
<h1>Destroyers</h1> 

<p>The workhorse of military units.  Relatively cheap and
quick, they are lightly armored and relatively expendable.</p>
"""

cruisers_info = \
"""
<h1>Cruisers</h1>

<p>The smallest of the capital ships.  They are the smallest 
ship that require the use of scarce commodities (5 units of Krellmetal) to 
build.</p>

<p>Cruisers are the fastest military ships, designed for speed and attack,
they are relatively weak at defending themselves.  Best used in homogenous fleets as point
defense interceptors, or maybe mixed with a Blackbird to provide longer range sensors.</p>
"""

battleships_info = \
"""
<h1>Battleships</h1> 
<p>The classic capital ship.  Battleships larger and more powerful than cruisers, having a much 
better defense capability.  They are slower than cruisers however, and 
are much more expensive.</p>
"""
superbattleships_info = \
"""
<h1> Super Battleships</h1>

<p>Like battleships, but bigger, faster, more expensive...</p>
"""

carriers_info = \
"""
<h1>Carriers</h1>

<p>Large, thinly armored ships designed to carry fighters around.
ideally suited for attacking heavily defended targets (as long as they are
carrying fighters...)</p>
"""

introduction_help = \
"""
<h1> Hello! </h1>

<h3> Introduction </h3>
<p>Dave's Galaxy is, I hope, a very carefully designed and 'deep' game.  
There is no real right way to play the game, I have seen several different,
interesting, totally different ways of playing the game well.</p>

<p>One player created a Stalinistic gulag, another built a trade network with
his neighbors, and a third became a pirate king.  Think about what you want
to be, and attempt to do that.  There are no phony quests, and no badly written
back story.</p>

<p>The premise of the game is that you are the leader of an alien civilisation
that has just achieved interstellar travel.  Try to create a novel alien race
in your head, and attempt to be it.  Invent your own version of fractured english
to use when talking to your neighbors.  Have a strange preoccupation with your
ovipositor.  BE WEIRD.  Dave's Galaxy can be a true Role Playing Game in the
original sense of the term, if you play it that way.</p>

<h3> Winning </h3>
<p>There is no real winning condition in Dave's Galaxy.</p>

"""

tutorial1_help = \
"""
<h1> Tutorial Part 1</h1>

<p>Ok. So you have the game running, and if this is your first time
playing, there should be an arrow pointing at a star saying 'you are here!'.
This is your home star system.  There should be <a href="/help/planetrings/">two solid 
rings and a dashed ring</a> around the star.</p>

<p>If you don't like the color of the rings around your star, you can change
that in the preferences tab at the top of the screen.</p>

<h3>Start a Colony</h3>

<p>Most players want to start some colonies on their first turn, and no matter
what you want to do later on, this is probably still a good idea.</p>

<ol>
  <li>
    Left click on your star.  (it will increase in size slightly if you 
    hover over it).
  </li>
  <li>Choose 'Build Fleet' from the menu.</li>
  <li>Find 'Arc' in the list. (This is a colony ship).</li>
  <li>Click on the '+' button, and 'Build Fleet'.</li>
  <li>An arrow should appear under the mouse pointer, hover the mouse over
  the nearest star and left click on it.</li>
  <li> The fleet will move towards the star when the next turn starts.</li>
</ol>
<p>Continue on to <a href="/help/tutorial2/">Tutorial, Part 2</a></p>
"""

tutorial2_help = \
"""
<h1> Tutorial Part 2 </h1>

<h3> Take a look at your neighbors</h3>
<p>You will have at least one neighbor.  You can find neighbors either by 
panning around on the map (just click and drag anywhere on the map 
that isn't a star or fleet), or click on the "Neighbors" tab on the left, and
then hit the goto button -- 
  <img width="12" height="12" class="noborder" src="/site_media/center.png"/></p>

<p> New neighbors may appear randomly on your borders over time, this is
the nature of the universe.</p>

<h3> Communicating </h3>
<p> You should communicate with your neighbors.  Click on the messages tab
at the top right of the screen, and send messages to your new neighbors.  You
can only communicate with players who are your neighbors in Dave's Galaxy.
To get more neighbors, send a fleet (or diplomatic mission if you will...) in
their direction.</p>

<h3> Upgrades </h3>
<p> Every star system can have various upgrades built on it.  If this is your
first turn, you probably do not want to buy one right now, but in a few turns,
you will probably want to buy a slingshot, which launches your ships with a higher
velocity than they can attain on their own.</p>

<p> you can find what upgrades are currently on your stars either by 
left clicking on the star, and choosing 'Upgrades', or through the
Planets tab on the left of the screen -- click on the upgrades button
<img class="noborder" 
     src="/site_media/upgradebutton.png" 
     width="12" height="12"/>.</p>

<p>Continue on to <a href="/help/tutorial3/">Tutorial, Part 3</a></p>
"""

tutorial3_help = \
"""
<h1> Tutorial Part 3 </h1>
<h3> Sensor Range </h3>
<img width="187" 
     height="214" 
     style="float:right;" 
     class="smallborder" 
     src="/site_media/sensering.png"/>
<p>If you look at your star(s) and fleets, they will have a large, 
darker circle around them, this is how far the sensors of that 
fleet/star can see.</p>

<p>As your stars become more technically advanced, the distance that 
they can see grows, if two stars are close together but their sensor 
ranges don't touch, they may grow close enough over time to touch.</p>

<h3> Defense </h3>
<p> Early in the game, you probably won't run into your neighbors for
several turns.  Defense is not terribly important at this point, but
eventually you will want to start building a defense for your growing
empire.</p>

<p>Defense can take many forms.  You can concentrate all your ships
in one large fleet, make many smaller fleets, build skirmish lines,
whatever you want.  I would give details, but part of the fun of
games, I think, is to learn for yourself.</p>
<p>Continue on to <a href="/help/tutorial4/">Tutorial, Part 4</a></p>
"""

tutorial4_help = \
"""
<h1> Tutorial Part 4 </h1>
<h3> Trade </h3>
<p> Once you have established colonies, you will want to set up a
trade network to support them.</p>

<p> Trade in Dave's Galaxy is very simple; you build a fleet with
Merchantmen in it, and send it towards another star.  On it's own,
the fleet will move from star to star buying and selling commodities,
and attempting to maximize it's profits.  Periodically it will
return to it's home port, and render profit to it's owner.</p>

<h3> Have Fun! </h3>
<p> Please, enjoy yourself playing Dave's Galaxy.  I have spent many
hours trying to make this the best game I can, and I hope you derive as
much joy in playing the game, as I have had in making it.</p>
"""




moving_help = \
"""
<h1>Moving Around</h1>

<h3>Panning</h3>
<p>Left click, and drag to pan.  Or you can use the arrow keys.</p>

<h3>Zooming</h3>
<p>There's a zoom control at the top left of the screen, click on + and - (or
the dots) to zoom in and out.  The plus and minus keys work as well.</p>

<h3>Go to a Specific Planet</h3>
<ol>
  <li>Click on the 'Planets' tab on the left of the screen</li>
  <li>Find the Planet in the list</li>
  <li>Click on the goto button -- 
    <img width="12" height="12" class="noborder" src="/site_media/center.png"/>
  </li>
</ol>

<h3>Go to a Specific Fleet</h3>
<ol>
  <li>Click on the 'Fleets' tab on the left of the screen</li>
  <li>Find the Fleet in the list</li>
  <li>Click on the goto button -- <img width="12" height="12" class="noborder" src="/site_media/center.png"/></li>
</ol>

<h3>Go to a Specific Neighbor</h3>
<ol>
  <li>Click on the 'Neighbors' tab on the left of the screen</li>
  <li>Find the Neighbor in the list</li>
  <li>Click on the goto button -- <img width="12" height="12" class="noborder" src="/site_media/center.png"/></li>
</ol>
"""

turns_help = \
"""
<h1>Turns</h1>
<p>Currently, turns happen once a day, from 5-5:30am PST (1300-1330 GMT).</p>

<p>I assume that this is inconvenient for some people, but it will be inconvenient
for some people no matter when it's done, so that's when it's done.</p>

<p>The game makes a vain attempt to shut down player interaction during this time,
so please let it do it's thing.</p>

<h3>Order of Events</h3>
<ol>
  <li>Neighbors are Determined</li>
  <li>Planet Update
    <ol>
      <li>Build Upgrades (if not finished)</li>
      <li>Resource Production</li>
      <li>Regional Taxation</li>
      <li>Fleet Upkeep</li>
    </ol>
  </li>
  <li>Remove Destroyed Fleets (from previous turn)</li>
  <li>Fleet Update
    <ol>
      <li>Move Enroute Fleets</li>
      <li>Advantage Discovery (if a fleet arrives at an unvisited star)</li>
      <li>Colony Creation</li>
      <li>Trade</li>
      <li>Planetary Assault (if at war with nearby star's owner)</li>
    </ol>
  </li>
</ol>


"""

diplomacy_help = \
"""
<h1>Diplomacy</h1>

<p>There are 3 states of Diplomacy in Dave's Galaxy; Alliance, Neutrality,
and War</p>

<h3>Alliance</h3>
<p> If you make an alliance with another player, you basically agree to
defend each other from all enemies, and to share all information on fleets.</p>

<p> To create an alliance, go to the Neighbors tab on the left, and click on 
'Offer Hand of Friendship'.  It will prompt you for a reason to create an
Alliance.  This message will be sent to the other player, who must agree to 
start the alliance.</p>

<h3>Neutrality</h3>
<p>This is the default state of diplomacy.  You can't see what the other
player is doing, unless he's within your sensor range.  Your ships will
not attack each other, but piracy can still happen </p>

<h3>War</h3>
<p>If at war with another player, any time a fleet comes in range
of another, combat will occur.  If you set a fleet's destination to a star
owned by your opponent, the fleet will assault the star system on arrival, 
and eventually conquer it (if the other player doesn't put up a 
defense...)</p>

<p>To end a War, click on 'Beg for Peace' in the Message tab, and
send a message to the opposing player, explaining why he should end the war.</p>

<p><i>War does not determine who is right - only who is left.</i>  
~ Bertrand Russell</p>
"""

ecodev_help = \
"""
<h1> Economic Development</h1>

<h3>Introduction</h3>
<p>As your stars mature, they gain in population and the technological level
of society increases.  Some commodities become more common over time, others 
become less common.</p>

<p>There are many ways you can effect these changes over time.  Trade evens
out production across star systems by moving goods that are common on one star,
to stars were they are less common.  There are Planet Upgrades that affect
production of commodities as well.</p>

<h3>Society Level</h3>
<p>Production of resources are controlled by the star system's Society Level and
population.  Surplus resources are produced if the people in a star system are able
to produce more than they use during a turn.</p>

<h3>Production Curves</h3>
<a href="/help/resourcegraph/">
  <div class="info2" style="float:right;">
    <img width="200" height="72" 
         class="smallborder" 
         src="/site_media/resources.png"/>
  </div>
</a>
<p>If a star system is left alone, except for buying Matter Synth 1&amp;2, it's 
production curves look like this graph.  If you look at the larger version, you'll see
that some resources get used up, while others become more common over time.</p>
"""

resourcegraph_help = \
"""
<h1> Graph of Resource Production Over Time </h1>
<img src="/site_media/resources-large.png"
     class="noborder"
     width="800" height="287"/>
"""

glossary_help = \
"""
<h1> Glossary </h1>

<h3> Fleet </h3>
<p> Fleets are made up of 1 or more ships.  a single ship is still a fleet, and is
capable of all the actions of a whole fleet.
</p>

<h3>Krell Metal</h3>
<p>Krell Metal is the easier of the two artificial elements to make.  It allows
you to build truly effective military ships, amongst other things</p>

<h3> Planet </h3>
<p>Planet and Star are interchangeable.  Every star you see on the map is considered
an inhabitable star system (or planet).</p>

<h3> Quatloo </h3>
<p>The galaxy-wide unit of 
<a href="http://en.wikipedia.org/wiki/The_Gamesters_of_Triskelion">currency</a>.</p>

<h3> Star </h3>
<p>See Planet.</p>

<h3> Unobtanium </h3>
<p> Unobtanium is an artificial element, and very hard to produce.  It is used
in ship production in very small amounts to improve offensive and defensive
systems.</p>
"""

planetrings_help = \
"""
<h1>Rings</h1>

<img width="200" 
     height="200" 
     style="float:right;" 
     class="smallborder" 
     src="/site_media/militaryrings.png"/>
<h3>Military Rings</h3>
<p>The military rings show you what kinds of ships can potentially be built
in a star system.  This is determined by whether there is Unobtanium and
Krell Metal (usually provided by Matter Synth 1/2) and a Military Base at
that location.</p>

<p>Thin dashed ring -- <a href="/help/mattersynth1/">Matter Synth 1</a>.</p>

<p>Thick dashed ring -- <a href="/help/mattersynth2/">Matter Synth 2</a>.</p>

<p>Longer Dashes -- <a href="/help/militarybase/">Military Base</a>.</p>

<img width="200" 
     height="100" 
     style="float:right;" 
     class="smallborder" 
     src="/site_media/rglgovt.png"/>
<h3>Regional Government</h3>
<p> Planets with a <a href="/help/rglgvt/">Regional Government</a>
get a grey ring showing their zone of taxation.</p>

<p> All other star systems you own in this ring will pay taxes to the star with
Regional Government.  If a star falls within range of two Regional Governments,
it will pay taxes to both.</p>

<h3>Food Scarcity</h3>
<p>Planets with Food Scarcity have a yellow ring, Famine shows
as a red ring.</p>

"""


connections_help = \
"""
<h1>Connections Between Stars</h1>

<h3>Empty Space</h3>
<p>There are places in the galaxy that are relatively empty of stars.
If two stars are reasonably far apart, and there are no stars too
close to a line drawn between them, a connection may be formed between
the two.</p>

<h3>How They Form</h3>
<img width="220" 
     height="140" 
     style="float:right;" 
     class="smallborder" 
     src="/site_media/connection.png"/>
<p>The conceit is that these connections are disturbed if another star
is close to the connection, or if another connection crosses it.  There
can also be no connections between stars owned by different players.</p>

<p>Connections are randomly determined when you build a new colony at a
star and can only change if you lose that star.</p>

<h3>What They Do</h3>
<p>Connections allow you to instantaneously move commodities from star
to star.  People have to still use ships, they cannot pass through
a connection (make up your own reason, radiation?).</p>

"""

markdown_help = \
"""
<div>
  <h1> Formatting Help </h1>
  <div>
    Dave's Galaxy uses Markdown syntax, 
    for a more detailed  tutorial, take a look at the
    <a href="http://en.wikipedia.org/wiki/Markdown">Wikipedia markdown entry</a>, 
    or the <a href="http://daringfireball.net/projects/markdown/syntax">developers
    documentation</a>.
  </div><div> </div>
  <div>paragraphs are separated by an empty line (extra carriage return)</div><hr/>

  <div>*emphasis* (italics)</div>
  <div>**strong emphasis** (boldface)</div><hr/>

  <div> - bulleted</div>
  <div> - list</div><hr/>

  <div> 1. enumerated</div>
  <div> 2. list</div><hr/>

  <div># heading</div>
  <div>## 2nd-level heading...</div>
</div>
"""

trade1_help = \
"""
<h1>Trade</h1>

<h3>Getting Started</h3>
<p> You can set up trade both inside and outside your empire.  Trade
is mostly an automatic process, your trade fleets will travel around, 
attempting to buy and sell commodities in such a way as they make a 
profit.</p>

<p>Trade only occurs at inhabited stars, if you send a trade fleet to
a star that is not inhabited, it will arrive at that star, not buy or sell 
anything, and then find an inhabited star system to go to and start trading again.</p>


<p> To start trading is a reasonably simple process.  Build a fleet that 
includes at least one merchantman or bulk freighter, and send it towards
another inhabited star system:</p>

<ol>
  <li> Left click on the star. </li>
  <li> Choose 'Build Fleet'.</li>
  <li> Click on the '+' button on the same line as Merchantmen
       or Bulk Freighter.</li>
  <li> Click on 'Build Fleet'.</li>
  <li> An arrow should appear under your mouse cursor, left click on
       another inhabited star system and the fleet will go there to
       start trading.</li>
</ol>

<p>(inhabited star systems have at least one ring around them)</p>

<p><a href="/help/trade2">Continue on to Trade Part 2</a></p>
"""

trade2_help = \
"""
<h1>Trade Part 2</h1>

<h3>International Trade</h3>
<p>If you have a neighbor who allows it, you can trade with his
stars as well, and this will happen automatically, as long as you
are not at war.</p>

<p>This can cause you problems when your ships start to go
places that you never planned for them to go, so be on the lookout
for piracy and accidentally wandering into a war zone.</p>

<h3>Profits, Fees</h3>
<p>Fleets will periodically return to their home star system to
render profit and taxes to their owner and government.  They also
pay a small fee every turn to the government of their home port.</p>
"""




piracy_help = \
"""
<h1>Piracy</h1>

<h3>How to Do it.</h3>
<p>Piracy itself is very simple.  Build a fleet that has some attack
strength, set it's disposition to Piracy, and put it somewhere
that it's likely to find defenseless ships to attack.</p>

<h3>Being Sneaky</h3>
<p>The best ship to use for Piracy is the <a href="/help/subspacers">Subspacer</a>.
It allows you to make your way through the other player's defenses 
without (hopefully) being seen.</p>


<h3>Piracy Itself</h3>
<p>There are some general rules for piracy, things you might want
to know.</p>
<ul>
  <li> Piracy respects alliances (the other player can see you
       sneaking around anyway).</li>
  <li> If a military fleet sees a Pirate fleet, it will attack it,
       unless you have an alliance with the other player.</li>
  <li> There are several outcomes of piracy.
    <ol>
      <li> The target fleet can escape, dropping it's cargo for the
           pirate to collect.</li>
      <li> The target can fight back.</li>
      <li> Or it can capitulate.  If it capitulates, it becomes
           the property of the pirate fleet's owner, joins the pirate
           fleet, and behaves in every way like he owns it.</li>
    </ol>
  </li>
</ul>
"""

routes_help = \
"""
<h1>Routes</h1>

<h3>Make your ships go around things</h3>
<p>You can use routing to put military ships on patrols, and make complex
movements to get around defenses.  You can put trade ships on routes
to keep them trading on a fixed set of stars in a fixed order.</p>

<h3>Unnamed Routes</h3>
<p>If you start a route on a fleet, the game assumes the route is for that
fleet only.  If the route is not circular, it will go away when the fleet
reaches it's end point.  If you want the route to stay around after the
fleet reaches it's end point, click on the route and select RENAME ROUTE.</p>

<h3>Named Routes</h3>
<p> Named routes are generally started in the middle of space, or at
a star system.  Multiple fleets can be put on one named route easily (click on
fleet --> ONTO NAMED ROUTE...).  Named routes are not removed from the game
if they do not have a fleet on them.</p>

<h3>Building Routes</h3>
<p>To buid a multi leg route: click on a star, fleet, or empty space, and 
choose one of the build route options.  A white line will appear under
the mouse.  Click on the map were you want the route to go, and then hit the 
enter key when you are done.  If it's a named route, it will prompt you for 
a name.
</p>

"""

combat_help = \
"""
<h1>Combat</h1>

<h3>How to Fight With your Neighbors</h3>
<p>Combat happens between 2 fleets when the following requirements are 
met.</p>

<ol>
  <li>The Fleet owners are at war (or one of the fleets is a pirate.)</li>
  <li>One fleet can see the other</li>
  <li>One of the fleets is able to attack the other (and can see it.)</li>
</ol>

<h3>Damaged and Destroyed Fleets</h3>
<img width="213" 
     height="139" 
     style="float:right;" 
     class="smallborder" 
     src="/site_media/destroyed.png"/>
<p> If a fleet has lost ship(s) during the last turn, it will be surrounded
by a fading yellow disk, if it was destroyed in the previous turn, it will 
have a fading red disk.</p>

<h3>Large vs. Small Fleets</h3>
<p>If one fleet is at least 1 1/2 times the size of the other, it will only 
attack with some of it's force, in an attempt to save it's more important 
ships from destruction.</p>

<h3>Attack and Defense</h3>
<p>Each type of ship has an attack and defense value.  It's attack value is
equal to as many attacks it can make per combat (each attack has a 30% chance 
of hitting something).  If an attack is successful, the defender can use
up to 3 defences to defeat it (out of whatever total defense strength it has).
If a ship can't defend itself, or the attack gets past one of it's defenses,
it is destroyed.</p>


"""

helptopics = {
  'general':          {'index': 100,
                       'name': 'General Help'},

  'introduction':     {'index': 101,
                       'name': 'Introduction (Read Me First)',
                       'contents': introduction_help},
  
  'moving':           {'index': 102,
                       'name': 'Moving Around',
                       'contents': moving_help
                      },

  'turns':            {'index': 103,
                       'name': 'Turns',
                       'contents': turns_help
                      },

  'diplomacy':        {'index': 104,
                       'name': 'Diplomacy',
                       'contents': diplomacy_help
                      },
  
  'markdown':         {'index': 105,
                       'name': 'Message Formatting',
                       'contents': markdown_help 
                      },

  'glossary':         {'index': 106,
                       'name': 'Glossary',
                       'contents': glossary_help
                      },

  'tutorial':         {'index': 200,
                       'name': 'Tutorial'},

  'tutorial1':        {'index': 201,
                       'name': 'Tutorial Part 1',
                       'contents': tutorial1_help
                      },

  'tutorial2':        {'index': 202,
                       'name': 'Tutorial Part 2',
                       'contents': tutorial2_help
                      },
  'tutorial3':        {'index': 203,
                       'name': 'Tutorial Part 3',
                       'contents': tutorial3_help
                      },

  'tutorial4':        {'index': 204,
                       'name': 'Tutorial Part 4',
                       'contents': tutorial4_help
                      },

  'planets':          {'index':300,
                       'name': 'Planets'},

  'planetrings':      {'index':301,
                       'name': 'Planet Rings',
                       'contents': planetrings_help},

  'ecodev':           {'index': 302,
                       'name': 'Economic Development',
                       'contents': ecodev_help
                      },
  
  'connections':      {'index':301,
                       'name': 'Connections',
                       'contents': connections_help},
  
  'resourcegraph':        {'index': 303,
                       'name': 'Resource Graph',
                       'contents': resourcegraph_help,
                       'width': 800
                      },

  'split1':           {'index': 399,
                       'split': 1},
  'shiptypes':        {'index':500,
                       'name': 'Ship Types'},
 
  'scouts':           {'index': 501,
                       'name': 'Scout',
                       'contents': scouts_info},

  'arcs':             {'index': 502,
                       'name': 'Arc',
                       'contents': arcs_info},

  'merchantmen':      {'index': 503,
                       'name': 'Merchantmen',
                       'contents': merchantmen_info},

  'fighters':         {'index': 504,
                       'name': 'Fighter',
                       'contents': fighters_info},

  'frigates':         {'index': 505,
                       'name': 'Frigate',
                       'contents': frigates_info},

  'cruisers':         {'index': 506,
                       'name': 'Cruiser',
                       'contents': cruisers_info},

  'battleships':      {'index': 507,
                       'name': 'Battleship',
                       'contents': battleships_info},

  'superbattleships': {'index': 508,
                       'name': 'Super Battleship',
                       'contents': superbattleships_info},

  'carriers':         {'index': 509,
                       'name': 'Carrier',
                       'contents': carriers_info},

  'destroyers':       {'index': 510,
                       'name': 'Destroyer',
                       'contents': destroyers_info},

  'blackbirds':       {'index': 512,
                       'name': 'Blackbird',
                       'contents': blackbirds_info},

  'subspacers':       {'index': 513,
                       'name': 'Subspacer',
                       'contents': subspacers_info},

  'bulkfreighters':  {'index': 514,
                       'name': 'Bulk Freighter',
                       'contents': bulkfreighters_info},

  'split2':           {'index': 699,
                       'split': 1},

  'fleets':           {'index': 700,
                       'name': 'Fleets'},

  'trade1':            {'index': 701,
                       'name': 'Trade Part 1',
                       'contents': trade1_help},

  'trade2':            {'index': 702,
                       'name': 'Trade Part 2',
                       'contents': trade2_help},

  'piracy':            {'index': 703,
                       'name': 'Piracy',
                       'contents': piracy_help},

  'combat':            {'index': 704,
                       'name': 'Combat',
                       'contents': combat_help},

  'routes':            {'index': 705,
                       'name': 'Routes',
                       'contents': routes_help},

  'planetupgrades':   {'index':800,
                       'name': 'Planet Upgrades'}}

for i in range(len(instrumentalitytypes)):
  t = instrumentalitytypes[i]
  helptopics[t['shortid']] = {'index':801+i,
                              'name':t['name'],
                              'contents': ''
                              }
  help = helptopics[t['shortid']]

  help['contents'] += \
  """
    <h1>%s</h1>
    <div>
      <div>
      </div>
      <div>
        <h3>Description</h3>
        <div>%s</div>
        <div class="info2" style="margin-top: 15px; float:right;">
          <img width="100" height="100" class="smallborder" 
               src="/site_media/instrumentality%sl.png"/>
          <div>%s</div>
        </div>
        <h3>Required Resources</h3>
        <table>
          <th class="rowheader">Resource</th><th class="rowheader">Amount</th>
  """ % (t['name'], t['description'], t['type'], t['name'])

  for r in t['required']:
    help['contents'] += '<tr><td>%s</td><td class="rowtotal">%d</td></tr>' % (r, t['required'][r])

  help['contents'] += \
  """
        </table>
      </div>
      <div>
        <h3>Upkeep</h3>
        <table>
          <tr><td>Upkeep, %% of GDP</td><td class="rowtotal">%2.2f%%</td></tr>
          <tr><td>Minimum Upkeep (Quatloos)</td><td class="rowtotal">%d</td></tr>
        </table>
      </div>
    </div>
  """ % (t['upkeep']*100.0, t['minupkeep'])




# build stats for ship type help (accel, attack/defense, 
# required resources, etc...)
for shiptype in shiptypes:
  print shiptype
  st = shiptypes[shiptype]
  help = helptopics[shiptype]
  help['contents'] += "<table><tr><td>"
  help['contents'] += "<h3>Stats:</h3>"
  help['contents'] += "<div class='info2'><table>"
  help['contents'] += "<tr><td>Acceleration</td><td style='color:yellow;'>%1.2f</td></tr>" % (st['accel'])
  help['contents'] += "<tr><td>Attack Strength</td><td style='color:yellow;'>%d</td></tr>" % (st['att'])
  help['contents'] += "<tr><td>Defense Strength</td><td style='color:yellow;'>%d</td></tr>" % (st['def'])
  help['contents'] += "<tr><td>Sensor Range</td><td style='color:yellow;'>%1.2f</td></tr>" % (st['sense'])
  help['contents'] += "</table></div>"

  
  help['contents'] += "<h3>Upkeep (1 turn):</h3>"
  help['contents'] += "<div class='info2'><table>"
  for u in st['upkeep']:
    help['contents'] += "<tr><td>%s</td><td style='color:yellow;'>%d</td></tr>" % (u, st['upkeep'][u])
  help['contents'] += "</table></div></td><td>"
  
  help['contents'] += "<h3>Build Cost</h3>"
  help['contents'] += "<div class='info2'><table>"
  for u in st['required']:
    help['contents'] += "<tr><td>%s</td><td style='color:yellow;'>%d</td></tr>" % (u, st['required'][u])
  help['contents'] += "</table></div></td></tr></table>"

for topic in helptopics:
  print str(topic)
  helptopics[topic]['id'] = topic

buildfleettooltips = [
  {'id': '#info-scouts', 'tip': scouts_info},
  {'id': '#info-arcs', 'tip': arcs_info},
  {'id': '#info-merchantmen', 'tip': merchantmen_info},
  {'id': '#info-fighters', 'tip': fighters_info},
  {'id': '#info-frigates', 'tip': frigates_info},
  {'id': '#info-cruisers', 'tip': cruisers_info},
  {'id': '#info-battleships', 'tip': battleships_info},
  {'id': '#info-superbattleships', 'tip': superbattleships_info},
  {'id': '#info-carriers', 'tip': carriers_info},
  {'id': '#info-destroyers', 'tip': destroyers_info},
  {'id': '#info-blackbirds', 'tip': blackbirds_info},
  {'id': '#info-subspacers', 'tip': subspacers_info},
  {'id': '#info-bulkfreighters', 'tip': bulkfreighters_info}]
