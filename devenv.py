from dragonfly import (Grammar, AppContext, MappingRule, CompoundRule, Choice, Dictation,
                       Key, Text, Function)


#---------------------------------------------------------------------------
# Create this module's grammar and the context under which it'll be active.

grammar_context = AppContext(executable="devenv")
grammar = Grammar("notepad_example", context=grammar_context)


#---------------------------------------------------------------------------
# Create a mapping rule which maps things you can say to actions.
#
# Note the relationship between the *mapping* and *extras* keyword
#  arguments.  The extras is a list of Dragonfly elements which are
#  available to be used in the specs of the mapping.  In this example
#  the Dictation("text")* extra makes it possible to use "<text>"
#  within a mapping spec and "%(text)s" within the associated action.

#stolen from http://dragonfly-modules.googlecode.com/svn/trunk/command-modules/documentation/mod-_multiedit.html

#SomeWords
def format_studly(text, preamble="", postamble=""):
    text = str(text)
    words = [word.capitalize() for word in text.split(" ")]
    Text(preamble + "".join(words) + postamble).execute()

#someWords	
def format_wimpy(text, preamble="", postamble=""):
    text = str(text)
    words = text.split(" ")
    words = words[0] + "".join(w.capitalize() for w in words[1:])
    Text(preamble + "".join(words) + postamble).execute()

#http://en.wikipedia.org/wiki/CamelCase#Variations_and_synonyms

example_rule = MappingRule(
    name="example",    # The name of the rule.
    mapping={          # The mapping dict: spec -> action.
			
			#Basic visual studio usage
			"save all":            Key("cs-s"),
			"build and run": Key("f5"),
			
			#Formatting
			"wimpy <text>": Function(format_wimpy),
			"studly <text>": Function(format_studly),
			
			#Resharper
			"super jump <text>": Key("c-t") + Text("%(text)s"),
			"refactor": Key("cs-r"),
			"rename": Key("c-r") + Key("c-r"),
			"quick fix": Key("a-enter"),
			"quick quick fix": Key("a-enter") + Key("enter"),
			
			#Declaration
			"public class <text>": Function(format_studly, preamble="public class ", postamble="\n{}"),
			"private class <text>": Function(format_studly, preamble="private class ", postamble="\n{}"),
			
			#coding
			"auto <text>": Function(format_wimpy, preamble="var ", postamble=" = "),
			"comment <text>": Text("//%(text)s"),
			"console dot write line": Text("Console.WriteLine("),
			"implements <text>": Function(format_studly, preamble=" : "),
			
			#nunit
			"assert equal": Text("Assert.AreEqual("),
			


			
            },
    extras=[           # Special elements in the specs of the mapping.
            Dictation("text"),
           ],
    )
grammar.add_rule(example_rule)

class CreateFnRule(CompoundRule):
	spec = "<access> <type> <text>"
	extras = [
		Choice("access", {
			"public": "public",
			"private": "private",
			"protected": "protected",
		}),
		#TODO: generate the list of types some how
		Choice("type", {
			"int": "int",
			"float": "float",
			"string": "string",
			"void": "void",
			"SubTexture2D": "SubTexture2D",
		}),
		Dictation("text")
	]
	def _process_recognition(self, node, extras):
		format_studly(extras["text"], extras["access"] + " " + extras["type"] + " ", "(")

grammar.add_rule(CreateFnRule())

#---------------------------------------------------------------------------
# Load the grammar instance and define how to unload it.

grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None