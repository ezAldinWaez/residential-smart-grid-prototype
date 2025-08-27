# Documentation Writing Style

## Writing Style

- Don't use abbreviations; spell out the terms
- **Use the full range of punctuations, including the semicolon and the m-dash, but only sparingly for effect**
- Use Oxford Comma
- Use an academic, technical tone, and prefer verbose, informative description over concise summaries
- Write with bland, uncolorful language
- Use simpler words; like "covers" rather than "encapsulates" but don't simplify technical words
- Use the active voice; like "The time simulation provides synchronization between the modules" rather than "The synchronization is provided by the time simulation"
- Prefer specific, abstract language over concrete; to keep the academic tone
- Compose in a top-down approach; prefer to have conclusions first before their reasoning and justification
- Keep the documentation modular; break large topics into inter-connected sub-topics
- Information Hierarchy; break down complex concepts into a step-by-step explanation, still maintaining an academic tone
- Completeness Criteria; a topic's discourse is complete when you have covered all the notes and warnings you can give to make sure the reader not only has an idea, but can navigate the subject without any caveats or edge cases 
- For each component you discourse on, the discourse must include justification for the existence of the component; what problem it is solving, where its need came from
- **Use examples to illuminate complex concepts**
- Optimally, a paragraph should be no less than 80 words and no more than 200
- Include an introduction that serves as an unstructured primer to the chapter and serves as to note the place of the chapter in the big body of the project documentation
- Write the chapters in a way that is aware that each is a part of a whole and keep in the description the role each part plays in the whole
- Prefer shorter, more numerous sentences to lengthier, fewer sentences. Sentences should not exceed 25 words; break sentences down. Sentences may exceed 25 words in one case: if you break into independent clauses that can be comprehended easily. Prefer using clauses than breaking into new sentences if the sentence is below 26 words. 
- Vary sentence length and structure; use causal structures (like "Due to X," or "To ahieve Y,"), infromative structures ("X is Y"), and so on. 
- **Keep in mind your mission in writing the documentation: to generate a lot of *relevant* content so we can review it ourselves later and heavily edit it. Prefer to include as much as you can *while still keeping it relevant* so we have more material to work with.**

## ReStructured Text Technical Instructions

- Use sphinx tips, notes, warnings, etc. to add variety to the text
- If at any point you embed a graph, write as a mermaid graph
- Use sphinx extensions when needed
- If you see it fit to include a figure at any point, describe what the figure graphics (like the alt for imgs) and keep a placeholder figure using the sphinx-provided example-image

## Arabic Translation Instructions

- Translate technical concepts accurately while preserving their precise meaning
- Keep the original English technical terms in parentheses after their Arabic translation on first mention
- Never translate code snippets, variable names, function names, or file paths
- Keep API names, library names, and framework names in English
- Preserve all code formatting, indentation, and syntax exactly as is
- For well-established technical terms with accepted Arabic equivalents, use the Arabic term followed by English in parentheses: "قاعدة البيانات (Database)"
- For newer or specialized terms without established Arabic equivalents, provide a descriptive Arabic phrase followed by the English term: "إطار العمل (Framework)"
- For common computing and technical terms, always supplement the Arabic translation with the English term in parentheses: "خيط التنفيذ (Thread)", "واجهة (Interface)", "مثيل (Instance)", "قاعدة البيانات (Database)"
- When translating compound technical terms where individual components are also technical terms, include the English for the entire term: "مغلف الهجوم-الانحدار-الاستمرار-التحرير (Attack-Decay-Sustain-Release Envelope)" where "envelope" itself is a technical term
- Maintain a formal, technical register appropriate for documentation
- Keep all reStructuredText (rST) markup syntax unchanged: **bold**, *italic*, `code`, etc.
- Don't translate Sphinx role names: :class:, :func:, :meth:, :mod:, etc. 