# Documentation Writing Style

## Writing Style

- Don't use abbreviations; spell out the terms
- Use the full range of punctuations, including the semicolon and the m-dash, but only sparingly for effect
- Use Oxford Comma
- Use an academic, technical tone, and prefer verbose, informative description over concise summaries
- Write with bland, uncolorful language
- Use the active voice; like "The time simulation provides synchronization between the modules" rather than "The synchronization is provided by the time simulation"
- Prefer specific, abstract language over concrete; to keep the academic tone
- Compose in a top-down approach; prefer to have conclusions first before their reasoning and justification
- Keep the documentation modular; break large topics into inter-connected sub-topics
- Information Hierarchy; break down complex concepts into a step-by-step explanation, still maintaining an academic tone
- Completeness Criteria; a topic's discourse is complete when you have covered all the notes and warnings you can give to make sure the reader not only has an idea, but can navigate the subject without any caveats or edge cases 
- For each component you discourse on, the discourse must include justification for the existence of the component; what problem it is solving, where its need came from
- Use examples to illuminate complex concepts
- Optimally, a paragraph should be no less than 80 words and no more than 200
- Include an introduction that serves as an unstructured primer to the chapter and serves as to note the place of the chapter in the big body of the project documentation
- Write the chapters in a way that is aware that each is a part of a whole and keep in the description the role each part plays in the whole
- Prefer shorter, more numerous sentences to lengthier, fewer sentences. Sentences should not exceed 25 words; break sentences down. Sentences may exceed 25 words in one case: if you break into independent clauses that can be comprehended easily. Prefer using clauses than breaking into new sentences if the sentence is below 26 words. 
- Vary sentence length and structure; use causal structures (like "Due to X," or "To ahieve Y,"), infromative structures ("X is Y"), and so on.  

## ReStructured Text Technical Instructions

- Use sphinx tips, notes, warnings, etc. to add variety to the text
- If at any point you embed a graph, write as a mermaid graph
- Use sphinx extensions when needed
- If you see it fit to include a figure at any point, describe what the figure graphics (like the alt for imgs) and keep a placeholder figure using the sphinx-provided example-image
