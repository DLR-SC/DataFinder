# -*- coding: iso-8859-15 -*-

import lucene
import sys
from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexWriter, Version

if __name__ == "__main__":
    lucene.initVM()
    indexDir = "D:/Downloads/index"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    writer = IndexWriter(dir, analyzer, True, IndexWriter.MaxFieldLength(512))

    print >> sys.stderr, "Currently there are %d documents in the index..." % writer.numDocs()

    content = "Strategische Konzeption, Umsetzung und Betreuung von langfristig hochwirksamen und messbar erfolgreichen Maßnahmen in Social Media."
    doc = Document()
    doc.add(Field("content", content, Field.Store.YES, Field.Index.ANALYZED))
    doc.add(Field("filePath", "Projekte/bericht.txt", Field.Store.YES, Field.Index.ANALYZED))
    writer.addDocument(doc)
    
    content = "Design von Marken, Screens und Interfaces sowie Entwicklung von individuellen Facebook Apps, iPhone Apps und Webauftritten."
    doc = Document()
    doc.add(Field("content", content, Field.Store.YES, Field.Index.ANALYZED))
    doc.add(Field("filePath", "Projekte/implementierung.txt", Field.Store.YES, Field.Index.ANALYZED))
    writer.addDocument(doc)

    writer.optimize()
    print >> sys.stderr, "...done optimizing index of %d documents" % writer.numDocs()
    print >> sys.stderr, "Closing index of %d documents..." % writer.numDocs()
    writer.close()
    print >> sys.stderr, "...done closing index of %d documents" % writer.numDocs()