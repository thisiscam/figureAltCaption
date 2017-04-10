"""
Generates a Caption for Figures for each Image which stands alone in a paragraph,
similar to pandoc#s handling of images/figures

--------------------------------------------

Licensed under the GPL 2 (see LICENSE.md)

Copyright 2015 - Jan Dittrich by
building upon the markdown-figures Plugin by
Copyright 2013 - [Helder Correia](http://heldercorreia.com) (GPL2)

--------------------------------------------

Examples:
    Bla bla bla

    ![this is the caption](http://lorempixel.com/400/200/)

    Next paragraph starts here

would generate a figure like this:

    <figure>
        <img src="http://lorempixel.com/400/200/">
        <figcaption>this is the caption</figcaption>
    </figure>
"""


from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import IMAGE_LINK_RE, IMAGE_REFERENCE_RE, NOBRACKET, BRK
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re #regex

import logging
logger = logging.getLogger('MARKDOWN')

FIGURES = [u'\s*'+IMAGE_LINK_RE+u'\s*', u'\s*'+IMAGE_REFERENCE_RE+u'\s*'] #is: linestart, any whitespace (even none), image, any whitespace (even none), line ends.

# This is the core part of the extension
class FigureCaptionProcessor(BlockProcessor):
    FIGURES_RE = re.compile('|'.join(f for f in FIGURES))
    def test(self, parent, block): # is the block relevant
        # Wenn es ein Bild gibt und das Bild alleine im paragraph ist, und das Bild nicht schon einen figure parent hat, returne True
        lines = block.split("\n")
        for line in lines:
            isImage = bool(self.FIGURES_RE.search(line))
            isInFigure = (parent.tag == 'figure')

            if not (isImage and not isInFigure):
                return False
        return True

    def run(self, parent, blocks): # how to process the block?
        raw_block = blocks.pop(0)

        lines = raw_block.split("\n")
        x = etree.SubElement(parent, 'div')
        for line in lines:
            captionText = self.FIGURES_RE.search(line).group(1)

            # create figure
            figure = etree.SubElement(x, 'figure')

            # render image in figure
            figure.text = line

            # create caption
            figcaptionElem = etree.SubElement(figure,'figcaption')
            figcaptionElem.text = captionText #no clue why the text itself turns out as html again and not raw. Anyhow, it suits me, the blockparsers annoyingly wrapped everything into <p>.

class FigureCaptionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        """ Add an instance of FigcaptionProcessor to BlockParser. """
        md.parser.blockprocessors.add('figureAltcaption',
                                      FigureCaptionProcessor(md.parser),
                                      '<ulist')

def makeExtension(configs={}):
    return FigureCaptionExtension(configs=configs)
