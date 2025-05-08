from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip
from anki.collection import SearchNode
from aqt.browser import SidebarItem, SidebarTreeView, SidebarItemType
from aqt.gui_hooks import browser_sidebar_will_show_context_menu
from anki.consts import DYN_OLDEST, DYN_RANDOM, DYN_SMALLINT, DYN_BIGINT, DYN_LAPSES, DYN_ADDED, DYN_DUE, DYN_REVADDED, DYN_DUEPRIORITY

# from typing import TYPE_CHECKING

def remapCards(deckName):
    mw.progress.start()
    col = mw.col
    # cache affected deck names
    modifiedDecks = set()
    modifiedDecks.add(deckName)

    # iterate through cards
    deck = col.decks.by_name(deckName)
    for cid in mw.col.find_cards(f'''deck:"{deckName}"'''):
        card = mw.col.get_card(cid)

        # Get template name
        templateName = ""
        for template in card.note_type()['tmpls']:
            if template['ord'] == card.ord:
                templateName = template['name']
                break
        if templateName == "":
            break
        
        # Construct deck name
        newDeckName = deckName + "::" + templateName
        modifiedDecks.add(newDeckName)
        print(newDeckName)

        # Get or create deck and did
        did = col.decks.id(newDeckName)
        deck = col.decks.get(did)
        col.decks.save(deck)

        # Reassign card to deck
        col.set_deck([cid], did)
        col.update_card(col.get_card(cid))
        
    # finish changes
    # Not sure if we need to rebuild the schedule or anything... the below code only works 
    # for filtered decks but there may be something similar we need to do

    # print(modifiedDecks)
    # for mod_deck in modifiedDecks:
    #     did = col.decks.id(mod_deck)
    #     col.sched.rebuildDyn(did)
    
    mw.progress.finish()


def remapCardsHandler(sidebar: "SidebarTreeView",  menu: QMenu, item: SidebarItem, index: QModelIndex):
    # Adds our option to the right click menu for tags in the deck browser
    if item.item_type == SidebarItemType.DECK:
        menu.addSeparator() 
        menu.addAction("Map card types to decks", lambda: remapCards(item.full_name) )
        

# Append our option to the context menu
browser_sidebar_will_show_context_menu.append(remapCardsHandler)