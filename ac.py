import ahocorasick

import string

import re

from pprint import pprint

import numpy as np

from collections import Counter

import unicodedata
import sys

# .translate( str.maketrans( "", "", string.punctuation ) ) is too weak; thanks https://stackoverflow.com/a/21635971
# string.punctuation += "“”";
# print( string.punctuation )
# stripPunctuation = str.maketrans( "", "", string.punctuation );
stripPunctuation = dict.fromkeys( i for i in range( sys.maxunicode ) if unicodedata.category(chr(i)).startswith('P') );

# thanks https://stackoverflow.com/a/13734572 ; captures both lan.split() and the index information for each split word, to ultimately recover punctuation
lan = open( "../HarryPotter1_hon_da_phu_thuy01-lan.txt", encoding="utf8" ).read();
lansp, lanspinds = zip( *[ ( m.group(0).lower().translate( stripPunctuation ), ( m.start(), m.end()-1 ) ) for m in re.finditer( r'\S+', lan ) ] );
joinedLansp = " ".join( lansp ); # thicc text within which to query stt substrings

stt = open( "../HarryPotter1_hon_da_phu_thuy01-stt.txt", encoding="utf8" ).read();
sttsp, sttspinds = zip( *[ ( m.group(0).lower().translate( stripPunctuation ), ( m.start(), m.end()-1 ) ) for m in re.finditer( r'\S+', stt ) ] );

print( "lan len:", len( lansp ), "words /", len( lan ), "chars; stt len:", len( sttsp ), "words /", len( stt ), end="\n\n\n" );






def acPass( wordBlockSize, blockBoundaries ):
	
	queries = { i: " ".join( sttsp[ i*blockBoundaries : i*blockBoundaries + wordBlockSize ] ) for i in range( 0, len( sttsp ) // blockBoundaries ) }; # math is hard but this gets an extra query at the end. bonus. nice.

	# remove duplicate queries (keep the first occurrance)
	seenQueries = set();
	uniqQueries = {};
	for i, q in queries.items():
		if q in seenQueries: continue;
		seenQueries.add( q );
		uniqQueries[ i ] = q;
	print( "block len:", wordBlockSize, ", block interval:", blockBoundaries, "=> num queries:", len( queries ), end="\n" )

	print( "removed duplicate queries:", str(len(queries)-len(uniqQueries))+"/"+str(len(queries)) );




	ac = ahocorasick.Automaton();
	for i, q in uniqQueries.items(): ac.add_word( q, ( i, q ) ); # gaps in index are fine and are needed to restore the original string positioning in splitInds (we removed some of the indexes)
	ac.make_automaton();

	# print( joinedLansp[ 203 : 251+1 ] )
	# print( queries[ 11 ] )
	# print( sttsp[ 11*blockBoundaries : 11*blockBoundaries + wordBlockSize ] )

	# lit = ( lansp[ len( joinedLansp[:203].split() ) : len( joinedLansp[:251].split() ) ] )
	# af = ( lanspinds[ len( joinedLansp[:203].split() ) : len( joinedLansp[:251].split() ) ] )

	# print( "in lan:", lan[af[0][0]:af[-1][1]+1] )
	# print( "in stt:", stt[sttspinds[11*blockBoundaries][0] : sttspinds[11*blockBoundaries+wordBlockSize-1][1]+1] )

	# take an aho corasick match, expand it, and return char ranges, split string ranges, and original texts for both lan and stt, in addition to the matchText
	def splitInds( joinedLanspStart, joinedLanspEnd, queryIdx ):
		# print( "\nSPLIT INDS", joinedLanspStart, joinedLanspEnd, queryIdx, "`" + joinedLansp[joinedLanspStart:joinedLanspEnd] + "`", queries[ queryIdx ] )

		# joinedLansp[ joinedLanspStart : joinedLanspEnd + 1 ] == queries[ queryIdx ] is the matching text
		sttspindRange = ( queryIdx * blockBoundaries, min( queryIdx * blockBoundaries + wordBlockSize, len( sttspinds ) ) ); # gives you original stt char indexes for each split word
		lanspindRange = ( len( joinedLansp[:joinedLanspStart-1].split(" ") ), min( len( joinedLansp[:joinedLanspEnd].split(" ") ), len( lanspinds ) ) );

		# if joinedLanspStart:joinedLanspEnd aren't on word boundaries, the queryIdx is matching in joinedLansp in the middle of a word, so the match has to contract until they're on word boundaries because reasons; bug where it matched [ khi, ... ] in the middle of cókhi in lan
		if sttsp[ sttspindRange[0] ] != lansp[ lanspindRange[0] ]: sttspindRange = ( sttspindRange[0] + 1, sttspindRange[1] ); # this seemed to fix it for every case that i have hit, should keep the following check just in case; since joinedLanspStart and joinedLanspEnd aren't used and since the expansion process happens anyway, it's fine to modify in this way
		
		if " ".join( sttsp[ slice( *sttspindRange ) ] ) != " ".join( lansp[ slice( *lanspindRange ) ] ):
			print( "!!! FAILED FOR SOME REASON !!!", "stt:", sttspindRange, "lan:", lanspindRange )
			print( "sttspindRange joined:", " ".join( sttsp[ slice( *sttspindRange ) ] ) )
			print( "lanspindRange joined:", " ".join( lansp[ slice( *lanspindRange ) ] ) )
			print( "stt", list( enumerate( sttsp ) )[sttspindRange[0]-10:sttspindRange[1]+10], "\nlan", list( enumerate( lansp ) )[lanspindRange[0]-10:lanspindRange[1]+10] )

		# print( 0, " ".join( sttsp[ sttspindRange[0] : sttspindRange[1] ] ), " ".join( lansp[ lanspindRange[0] : lanspindRange[1] ] ), sep="\n" ); # print the match

		# expand spindRanges
		while sttspindRange[0]-1 >= 0 and lanspindRange[0]-1 >= 0 and sttsp[ sttspindRange[0]-1 ] == lansp[ lanspindRange[0]-1 ]:
			sttspindRange = ( sttspindRange[0]-1, sttspindRange[1] );
			lanspindRange = ( lanspindRange[0]-1, lanspindRange[1] );
			# print( 1, str(sttspindRange) + " : " + " ".join( sttsp[ sttspindRange[0] : sttspindRange[1] ] ), str(lanspindRange) + " : " + " ".join( lansp[ lanspindRange[0] : lanspindRange[1] ] ), sep="\n" ); # print the match
		while sttspindRange[1] < len( sttsp ) and lanspindRange[1] < len( lansp ) and sttsp[ sttspindRange[1] ] == lansp[ lanspindRange[1] ]: # right range index is noninclusive
			sttspindRange = ( sttspindRange[0], sttspindRange[1]+1 );
			lanspindRange = ( lanspindRange[0], lanspindRange[1]+1 );
			# print( 2, str(sttspindRange) + " : " + " ".join( sttsp[ sttspindRange[0] : sttspindRange[1] ] ), str(lanspindRange) + " : " + " ".join( lansp[ lanspindRange[0] : lanspindRange[1] ] ), sep="\n" ); # print the match
		# print()

		sttOrigCharRange = ( sttspinds[ sttspindRange[0] ][0], sttspinds[ sttspindRange[1]-1 ][1] + 1 );
		lanOrigCharRange = ( lanspinds[ lanspindRange[0] ][0], lanspinds[ lanspindRange[1]-1 ][1] + 1 );

		return { "stt": { "spindRange": sttspindRange, "origCharRange": sttOrigCharRange, "text": stt[ sttOrigCharRange[0] : sttOrigCharRange[1] ] }, \
				 "lan": { "spindRange": lanspindRange, "origCharRange": lanOrigCharRange, "text": lan[ lanOrigCharRange[0] : lanOrigCharRange[1] ] }, \
				 "matchText": queries[ queryIdx ] };

	# pprint( splitInds( 219, 267, 12 ) )

	# for joinedLanspEnd, (queryIdx, query) in A.iter( joinedLansp ):
	# 	joinedLanspStart = joinedLanspEnd - len(query) + 1
	# 	print(joinedLanspStart, "-", joinedLanspEnd, ",", queryIdx, ",", query, "//", str( joinedLanspStart * 100 / len( lan ) ) + "%")
	# 	print( splitInds( joinedLanspStart, joinedLanspEnd, queryIdx ) )

	# this needs to check if any return matched multiple

	acRet = [ ( joinedLanspEnd, ( queryIdx, query ) ) for joinedLanspEnd, ( queryIdx, query ) in ac.iter( joinedLansp ) ];
	# print(acRet)
	acRetQIdxCounts = Counter( a[1][0] for a in acRet );
	print( "removed multimatches:", [ (q, cnt, queries[q]) for q, cnt in acRetQIdxCounts.items() if cnt != 1 ] )
	acRet = [ a for a in acRet if acRetQIdxCounts[ a[1][0] ] == 1 ]; # strip all matches which don't occur strictly once; fully remove all duplicates

	matchingSegments = [ splitInds( joinedLanspEnd - len( query ) + 1, joinedLanspEnd + 1, queryIdx ) for joinedLanspEnd, ( queryIdx, query ) in acRet ];

	print( "num matches:", str(len(matchingSegments)) + "/" + str(len(queries)) );

	# merge overlapping / duplicated matchings (since they've each been expanded in splitInds)
	duplicateStore = set();
	matchToRangeSet = lambda m: ( *m["lan"]["origCharRange"], *m["lan"]["spindRange"], *m["stt"]["origCharRange"], *m["stt"]["spindRange"] );
	matchingSegments = [ m for m in matchingSegments if matchToRangeSet( m ) not in duplicateStore and not duplicateStore.add( matchToRangeSet( m ) ) ]; # thanks https://stackoverflow.com/a/4463433


	# pprint( matchingSegments[:3] )
	return matchingSegments;



def matchQuality( matches ):
	unmatchBorders = [ 0, *[ m for match in matches for m in match[ "lan" ][ "spindRange" ] ], len( lansp ) ];
	wordGaps = [ r-l for (l,r) in list( zip( unmatchBorders[0::2], unmatchBorders[1::2] ) ) if r-l > 0 ]; # not sure if the r-l <= 0 case ever occurs now that i expand the matches
	# print( "word gaps:", wordGaps );
	print( "average gap:", np.mean( wordGaps ) );
	return wordGaps; # not very useful, should probably return the gap index ranges / complement of matches lan spindRange

# OH NO MY CODE IS BROKEN FOR BLOCK SIZE OF 3..5ish i think oh no

# matchQuality( acPass( wordBlockSize=12, blockBoundaries=4 ) );
# too small wordBlockSize fails because matches of that size can be unique in each text but still be wrong because of a mistranscription which screws up everything else. không phải là appears in each once yet they are at totally different sections of the chapter
matches = acPass( wordBlockSize=16, blockBoundaries=1 ); # aho corasick is just way too fast wtf lol
matchQuality( matches );

# pprint( matches );

# mismatch1Lan = ( matches[0]["lan"]["spindRange"][1], matches[1]["lan"]["spindRange"][0] )
# mismatch1Stt = ( matches[0]["stt"]["spindRange"][1], matches[1]["stt"]["spindRange"][0] )

# print( "\n\nfirst mismatch:", " ".join( lansp[ slice(*mismatch1Lan) ] ), " ".join( sttsp[ slice(*mismatch1Stt) ] ), sep="\n" )

print( "\n\n" )

for i in range( len( matches ) ):
	print( "✓lan        ", matches[i]["lan"]["text"].replace( "\n", "⏎" ) )
	print( "✓stt        ", matches[i]["stt"]["text"].replace( "\n", "⏎" ) )
	# print()
	if( i + 1 < len( matches ) ):
		print( "!LAN!----   ", lan[ matches[i]["lan"]["origCharRange"][1]+1 : matches[i+1]["lan"]["origCharRange"][0]-1 ].replace( "\n", "⏎" ) ) # origCharRange is right inclusive i think??
		print( "!STT!----   ", stt[ matches[i]["stt"]["origCharRange"][1]+1 : matches[i+1]["stt"]["origCharRange"][0]-1 ].replace( "\n", "⏎" ) )
	# print()

# i'm somehow missing the last word of the whole text. that's okay for now ig lol. not sure why.

# pprint( matches );

# matchQuality( matches )




lanMatchSpinds = [ m for match in matches for m in match[ "lan" ][ "spindRange" ] ];
lanMismatchSpinds = [ 0, *lanMatchSpinds, len( lansp ) ];
lanMismatchSpindRanges = list( zip( lanMismatchSpinds[0::2], lanMismatchSpinds[1::2] ) )

sttMatchSpinds = [ m for match in matches for m in match[ "stt" ][ "spindRange" ] ];
sttMismatchSpinds = [ 0, *sttMatchSpinds, len( sttsp ) ];
sttMismatchSpindRanges = list( zip( sttMismatchSpinds[0::2], sttMismatchSpinds[1::2] ) )

print("\n\n\n")
print( "stt", [ a for a, cnt in Counter( [ m for match in matches for m in match[ "stt" ][ "spindRange" ] ] ).items() if cnt > 1 ] )
print( list( zip( sttMatchSpinds[0::2], sttMatchSpinds[1::2] ) ) )

print( "lan", [ a for a, cnt in Counter( [ m for match in matches for m in match[ "lan" ][ "spindRange" ] ] ).items() if cnt > 1 ] )
print( list( zip( lanMatchSpinds[0::2], lanMatchSpinds[1::2] ) ) )


for i, sttMM in enumerate( sttMismatchSpindRanges ):
	lanMM = lanMismatchSpindRanges[ i ]

	# run acpass on sttMM and lanMM ranges
	# print( len( lansp[ slice( *lanMM ) ] ), " ".join( lansp[ slice( *lanMM ) ] ) )
	# print( len( sttsp[ slice( *sttMM ) ] ), " ".join( sttsp[ slice( *sttMM ) ] ) )
	# print("\n\n\n")


