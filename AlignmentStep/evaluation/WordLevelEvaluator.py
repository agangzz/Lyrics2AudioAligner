'''
Created on Mar 5, 2014

This metric is strict, because an error might be counted twice if end and begin of consecutive tokens coincide. 
This happens when there is no silent pause between tokens both in annotation and detected result. 
This is similar to proposed by shriberg on sentence boundary detection.  
@author: joro
'''

import os
import sys

from IPython.core.tests.test_formatters import numpy

# this allows path to packages to be resolved correctly (on import) from outside of eclipse 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
sys.path.append(parentDir)

from evaluation.TextGrid_Parsing import TextGrid2Dict, TextGrid2WordList
from utils.Utils import writeListOfListToTextFile, mlf2WordAndTsList, \
    mlf2PhonemesAndTsList, getMeanAndStDevError


ANNOTATION_EXT = '.TextGrid'
DETECTED_EXT = '.dtwDurationsAligned'

##################################################################################

# utility enumerate constants class 
class Enumerate(object):
  def __init__(self, names):
    for number, name in enumerate(names.split()):
      setattr(self, name, number)

tierAliases = Enumerate("phonemeLevel wordLevel phraseLevel")

'''
calculate evaluation metric
For now works only with begin ts
'''
def wordsList2avrgTxt(annotationWordList, detectedWordList):
    
    sumDifferences = 0;
    matchedWordCounter = 0;
    
    # parse annotation word ts and compare each with its detected
    for tupleWordAndTs in annotationWordList:
        for tupleDetectedWordAndTs in  detectedWordList:
            
            if tupleWordAndTs[1] == tupleDetectedWordAndTs[1]:
                currdifference = abs(float(tupleWordAndTs[0]) - float(tupleDetectedWordAndTs[0]))
                matchedWordCounter +=1
                sumDifferences = sumDifferences + currdifference
                # from beginning of list till first matched word
                break
    return sumDifferences/matchedWordCounter
            
            
            
    return


def evalAlignmentError(annotationURI, detectedURI, whichLevel=2  ):
    '''
Calculate alignment errors. Does not check token identities, but proceeds successively one-by-one  
Make sure detected tokens (wihtout counting sp, sil ) are same number as annotated tokens 

TODO: eval performance of end timest. only and compare with begin ts. 
@param whichLevel, 0- phonemeLevel, 1 -wordLevel,  2 - phraseLevel
    '''
    alignmentErrors = []
    
    ######################  
    # prepare list of phrases from ANNOTATION:
    
    annotationPhraseListA = TextGrid2WordList(annotationURI, whichLevel)     
    
    annotationPhraseListNoPauses = []
    for tsAndPhrase in annotationPhraseListA:
        if tsAndPhrase[2] != "" and not(tsAndPhrase[2].isspace()): # skip empty phrases
                annotationPhraseListNoPauses.append(tsAndPhrase)
    
    if len(annotationPhraseListNoPauses) == 0:
        sys.exit(annotationURI + ' is empty!')
    
    ####################### 
    # # prepare list of phrases/phonemes from DETECTED:
    if whichLevel == tierAliases.phonemeLevel:
        detectedWordList= mlf2PhonemesAndTsList(detectedURI)
    elif whichLevel == tierAliases.wordLevel or whichLevel == tierAliases.phraseLevel :
        detectedWordList= mlf2WordAndTsList(detectedURI)
    
    # remove deteted tokens NOISE, sil, sp entries from  detectedWordList
    detectedWordListNoPauses = []   #result 
    for detectedTsAndWrd in detectedWordList:
        if detectedTsAndWrd[2] != 'sp' and detectedTsAndWrd[2] != 'sil' and detectedTsAndWrd[2] != 'NOISE':
            detectedWordListNoPauses.append(detectedTsAndWrd)
    
    if len(detectedWordListNoPauses) == 0:
        sys.exit(detectedURI + ' is empty!')
    
    # TODO: The whole evaluation, not but numWords, but by word id. ISSUE: 19
  
    
    # find start words of annotationPhraseListNoPauses
    currentWordNumber = 0
    for tsAndPhrase in annotationPhraseListNoPauses:
       
        tsAndPhrase[2] = tsAndPhrase[2].strip()
        words = tsAndPhrase[2].split(" ")
        numWordsInPhrase = len(words)
        
        if numWordsInPhrase == 0:
            sys.exit('phrase with no words in annotation file!')
        
        if  currentWordNumber + 1 > len(detectedWordListNoPauses):
            sys.exit('more tokens (words/phrases/phonemes) detected than in annotation. No evaluation possible')
            
        currTsandWord = detectedWordListNoPauses[currentWordNumber]
        
        # TODO: refactor:  repeat instead of reapeating code 
        # calc difference phrase begin Ts
        annotatedPhraseBEginTs = tsAndPhrase[0]
        detectedPhraseBeginTs = currTsandWord[0]
        
        currAlignmentError = calcError(annotatedPhraseBEginTs, detectedPhraseBeginTs)
        alignmentErrors.append(currAlignmentError)
        
        # calc difference phrase end Ts
        annotatedPhraseEndTs = tsAndPhrase[1]
        detectedPhraseEndTs = currTsandWord[1]
        
        currAlignmentError = calcError(annotatedPhraseEndTs, detectedPhraseEndTs)
        alignmentErrors.append(currAlignmentError)
        
        #### proceed as many words in annotation as         
        currentWordNumber +=numWordsInPhrase
                
    return  alignmentErrors
        

def calcError(annotatedPhraseBEginTs, detectedPhraseBeginTs):
    currAlignmentError = float(annotatedPhraseBEginTs) - float(detectedPhraseBeginTs)
    currAlignmentError = numpy.round(currAlignmentError, decimals=2)
    return currAlignmentError      
    


def evalOneFile(annotationURI, detectedURI, evalLevel=tierAliases.phonemeLevel):
        ''' Main utility function
        ''' 
       
        if (len(sys.argv) != 4):
             print ("Usage:  {} {} {} {}".format(sys.argv[0], "annotationURI", "detectedURI", "tierAliases.phonemeLevel") ) 
             sys.exit();
       
        
        alignmentErrors  = evalAlignmentError(annotationURI, detectedURI, int(evalLevel))
        
        mean, stDev, median = getMeanAndStDevError(alignmentErrors)
        
        # optional
#         print "mean : ", mean, "st dev: " , stDev
        print  mean, " ", stDev
        
        
         ### OPTIONAL : open detection and annotation in praat. can be provided on request
#         openAlignmentInPraat(annotationURI, detectedURI, 0, audioURI)
        
        return mean, stDev,  median, alignmentErrors
    
    

##################################################################################

if __name__ == '__main__':
    
    
    
         
#     PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/goekhan/'
    PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/safiye/'
    
    audioName = '01_Olmaz_Part2_nakarat'
#     audioName = '02_Kimseye_Part6_nakarat'     
#     audioName = '02_Kimseye_Part1_zemin'     
#     
    annotationURI = os.path.join(PATH_TEST_DATASET,  audioName + ANNOTATION_EXT)
    detectedURI = os.path.join(PATH_TEST_DATASET,  audioName +  DETECTED_EXT)
     
#     annotationURI = '/Volumes/IZOTOPE/sertan_sarki/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme/21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme_meyan2_from_69_194485_to_79_909261.TextGrid'
#     detectedURI = '~//Downloads/blah'
#      
    mean, stDev,  median, alignmentErrors  = evalOneFile(sys.argv[1], sys.argv[2], sys.argv[3])
#     mean, stDev,  median, alignmentErrors  = evalOneFile(annotationURI, detectedURI, tierAliases.wordLevel)


    
    
    ############# FROM HERE ON: old testing code for word-level eval 
#     tmpMLF= '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde_nakarat2_from_192.962376_to_225.170507.phone-level.output'
#     listWordsAndTs = mlf2WordAndTsList(tmpMLF)
#   
#     
#     
#   
# # TODO: error in parsing of sertan's textGrid
#     textGridFile = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde.TextGrid'
# #     textGridFile='/Volumes/IZOTOPE/adaptation_data/kani_karaca-cargah_tevsih.TextGrid'
# #     textGridFile = '/Users/joro/Documents/Phd/UPF/Example_words_phonemes.TextGrid'
#     textGridFile = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade_gazel.wordAnnotation.TextGrid'
#     
#     
#     
#     
#     listWordsAndTsAnnot = TextGrid2WordList(textGridFile)
#     
#     
#     annotationWordList = [[0.01, 'sil'], [0.05, 'rUzgar'], [0.9,'Simdi']]
#     avrgDiff = wordsList2avrgTxt(annotationWordList,listWordsAndTs)
#     
#     
#     print avrgDiff
    