<h1>Dungeons and Dragons 5e</h1>
<h2>Analysis of Monsters</h2>
<p>There are many pages out there that allow you
to auto-create an encounter, particularily the page 
<a href="https://kobold.club/fight/#/encounter-builder">Kobold Fight Club</a>
. These encounter generators often work wonders, and streamline the creation of fights.
</p>
<img src="https://kobold.club/fight/images/logo.png" alt="Kobold Fight Club Logo" width="250", height="250"></img>
<p>This program uses Pandas and other Data Science tools to commit an analysis using the Kobold Fight Club's database of monsters, with permision from u/Asmor to
give a deeper look into: </p>
<ul>How the average monster looks, is the normal "bad guy" a powerful mythological creature, or just a skeleton with a sword?</ul>
<ul>How many monsters you might expect to fight over an adventurers life time</ul>
<ul>Which types of monsters are the toughest or weakest</ul>
<h4>Overall: What is the data that influences the monster selection offered in these encounter builders?</h4>

<p>Cleaning the data was an issue, with pandas converting some values that created outliers</p>
<p>Once the data was cleaned the analysis began, with generic information being printed about the differing types of monsters
</p>
- Humanoids made up the largest amount of monster characters, so an adventurer can expect to fight vaguely human foes most of the time
- Celestials are the toughest enemy on average, with a CR of 13 (Equivalent to a hard encounter for 4 level 10 characters!)
- Unsurprisingly the Tarrasque came out as the meatiest monster, though there where a few suprises, with the meatiest fiend being a valid contender (Zariel for those looking for a fiendish Tarrasque replacement)
- The group with the highest average initiative was the Celestials (those wings help):  however the group with the highest initiative in their standard deviation was the <b>OOZE</b> which came as a big surprise with a std of 3.52 initiative 

