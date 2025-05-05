QUERY_SEARCH_SYNTAX_DOCS: str = """
SearXNG Query Search syntax
SearXNG comes with a search syntax by with you can modify the categories, engines, languages and more. See the preferences for the list of engines, categories and languages.

! select engine and category
To set category and/or engine names use a ! prefix. To give a few examples:

search in Wikipedia for paris
!wp paris
!wikipedia paris

search in category map for paris
!map paris
image search
!images Wau Holland

Abbreviations of the engines and languages are also accepted. Engine/category modifiers are chain able and inclusive. E.g. with !map !ddg !wp paris search in map category and DuckDuckGo and Wikipedia for paris.
: select language
To select language filter use a : prefix. To give an example:

search Wikipedia by a custom language
:fr !wp Wau Holland

!!<bang> external bangs
SearXNG supports the external bangs from DuckDuckGo. To directly jump to a external search page use the !! prefix. To give an example:

search Wikipedia by a custom language
!!wfr Wau Holland

Please note, your search will be performed directly in the external search engine, SearXNG cannot protect your privacy on this.

!! automatic redirect
When mentioning !! within the search query (separated by spaces), you will automatically be redirected to the first result. This behavior is comparable to the “Feeling Lucky” feature from DuckDuckGo. To give an example:

search for a query and get redirected to the first result
!! Wau Holland

Please keep in mind that the result you are being redirected to can’t become verified for being trustworthy, SearXNG cannot protect your personal privacy when using this feature. Use it at your own risk.

Special Queries
In the preferences page you find keywords for special queries. To give a few examples:

generate a random UUID
random uuid

find the average
avg 123 548 2.04 24.2

show user agent of your browser (needs to be activated)
user-agent

convert strings to different hash digests (needs to be activated)
md5 lorem ipsum
sha512 lorem ipsum
"""
