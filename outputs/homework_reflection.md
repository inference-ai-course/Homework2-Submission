
## Notebook 01: Week 2 Orientation & Path Selection

**Completed:** 2026-04-05 16:48:57

Path selected: C — Hybrid (Claude + Ollama)
Default model: qwen3.5:27b

Rationale: [YOUR ANSWER HERE]

Example: I chose Path A (Claude) because I want to use the extended thinking
feature in Notebook 07 and don't have a GPU for running qwen3.5:27b locally.
The estimated cost is with

---

## Notebook 01: Week 2 Orientation & Path Selection

**Completed:** 2026-04-17 21:18:02

Path selected: B — Local (Ollama — llama3.2:latest)
Default model: llama3.2:latest

Rationale: I chose Path A (Claude) and C Ollama.

 Because I find the qwen3.5:27 needs 16GB RAM, but I do have 16GB RAM, but after distributed to applications, only 8GB 
 RAM available, which is not adequate to

---

## Notebook 01: Week 2 Orientation & Path Selection

**Completed:** 2026-04-20 19:00:00

Path selected: D — Google GenAI API (gemini-2.0-flash)
Default model: llama3.2:latest

Rationale: I chose Path D (Gemini) and A (Claude) and B (Ollama) .

 Because I find the qwen3.5:27 needs 16GB RAM, but I do have 16GB RAM, but after distributed to applications, only 8GB 
 RAM available, which i

---


## Notebook 02: Transformer Architecture Insights

**Completed:** 2026-04-27 19:55:26

### Experiment 1 — Scaled Dot-Product Attention

Q/K/V dimensions: 8/8/8
Tokens: ['The', 'cat', 'sat', 'here']

**What I observed when modifying the Q vector:**
Describe:
- What Q vector change did you make?
    Q[1] was changed to all zeros, all fives, and equal to K[2] in three separate experiments.

- How did the attention distribution for 'cat' change?
    When Q[1] was set to all zeros, model treats all tokens as equally relevant--25% attention to each token.
    When Q[1] was set to all fives, will result a sharp attention. One token that happens to have a slightly higher sum in its Key vector will likely capture 99% of the attention, while the others drop to near-zero.
    When Q[1] was set equal to K[2], the attention distribution was concentrated on the third token.

- What does this tell you about how Q vectors control what a token attends to?

    When Q[1] was set to all zeros, The model becomes "unsure" and simply averages all surrounding information to stay safe.
    When Q[1] was set to all fives, If Q is too generic (like all fives), the attention mechanism breaks down and just gravitates toward whatever token has the highest variance in its embedding
    When Q[1] was set equal to K[2], If Q is high in "verb-seeking" dimensions, it will attend to verbs; if it is high in "subject-seeking" dimensions, it will attend to nouns.

---

### Experiment 2 — Multi-Head Attention (BertViz)

My sentence: "The 3 most reliable tax declaration application."

**What I observed in the attention heads:**
Describe:
- Which words appear to have strong attention connections?
  3--most, reliable--most, tax--declaration
- Can you identify any heads that seem to focus on syntax vs. meaning?
  Syntax-Focused Heads care about how the words relate to each other grammatically.
  The 3 most is the Positional Head.
   applications is the Dependency Head.
   And . is the Delimiter Head.
- Does [CLS] (the first token) attend broadly or narrowly?
  In the first few layers (Layers 1–3), the [CLS] token attends broadly and relatively uniformly.

---

### TODO 3 — Architecture Question

My question: Why does Layer Normalization in Transformers normalize across the feature dimension
(not the batch dimension like BatchNorm)?  What goes wrong if you use BatchNorm instead?

**What I learned:**
[YOUR REFLECTION HERE]

- What did you ask about?
    LN vs BN
- What did you learn from the answer?
 Use BN when:
Have large batch sizes
Typical in CNNs (images)
Training is stable with batches
Use LN when:
Batch size is small or varies
Using Transformers / NLP models
Want consistency between training & inference

- How does this connect to what we implemented in experiments 1–4?

If results are unstable → try switching BN → LN
If have large, consistent batches → BN can give slightly better performance
If unsure → LN is the safer default (especially in modern models)

---

## Notebook 03: Tokenization & Cost Analysis

**Completed:** 2026-04-28 16:49:06

### Tokenizer Comparison

Demo text token counts:
- tiktoken cl100k_base: 30 tokens
- HF gpt2: 30 tokens
- SentencePiece T5: 33 tokens

**My text comparison (TODO 1):**
- What text did you use? Why did you choose it?
 summary this website https://www.skool.com/solo-profits-growth-3578/classroom/7b3df2fd?md=563e6f7c886f424da0c71fa3972df373
 Because in my project of summary github readme, I need to summary the website content, so I want to know how many tokens will be used if I summary the website content.
- Which tokenizer was most efficient (fewest tokens)?
tiktoken's cl100k_base was the most efficient, with 49 tokens.
- Were you surprised by any splits? (Use the first_10_ids to inspect)
Yes, I was surprised by the splits. For example, the URL was split into multiple tokens, 
which increased the token count significantly. The tokenizer treated different parts of the URL as separate tokens, 
which is something I hadn't anticipated.

---

### BPE Deep-Dive (TODO 2)

- For which sentence types does gpt2 use more tokens than tiktoken? Why?
 python code and multilingual sentences show a larger difference, with gpt2 using more tokens. 
 This is likely because gpt2's tokenizer has a smaller vocabulary and may split code and non-Lang in text into more tokens,
  while tiktoken's cl100k_base can represent these more efficiently with fewer tokens.
- cl100k_base (tiktoken) has 100K vocab vs gpt2's 50K vocab — how does that affect efficiency?
    The larger vocabulary of cl100k_base allows it to represent a wider range of words and subwords as single tokens, 
    which can lead to fewer tokens for the same text compared to gpt2's smaller vocabulary. 
    This means that cl100k_base can be more efficient in terms of token count, especially for texts that include less common words, code, or multilingual content.

- If you're using Claude (which uses a similar vocab to cl100k), what does this mean for cost estimation?
    If using Claude, which has a similar vocabulary to cl100k, it means that the token counts get from tiktoken's cl100k_base will be a good estimate for the tokens that Claude will use. 
    This allows for more accurate cost estimation when using Claude, as you can directly apply the token counts from tiktoken to calculate potential costs based on Claude's pricing.

---

### Token Budget for My Project (TODO 3)

My prompt: 27 tokens
Expected output: 500 tokens

[YOUR REFLECTION HERE]

- What is the estimated cost per call for your project?
  The estimated cost per call for my project is approximately $0.003 for haiku, $0.007 for sonnet, and $0.04 for opus, 
  based on the token counts and pricing.

- How does this affect your model choice (Haiku vs Sonnet vs Opus)?
  Given the estimated costs, I would likely choose haiku for development and testing due to its lower cost, 
  and then consider sonnet for more refined outputs if the budget allows. 
  Opus may be too expensive for regular use in this project unless the quality improvement justifies the cost.

- Can you reduce token count without losing important information?
  To reduce token count, I could try to make the prompt more concise by removing unnecessary words or details,
  while still conveying the essential information needed for the model to generate a good response.
  For example, I could trim the prompt to focus on the key aspects of the GitHub README that I want summarized, 
  rather than including the entire URL or extraneous context.


- What's your total estimated API budget for the semester project?
  Based on the estimated cost per call and an expected number of calls, 
  I would set a total API budget of around $20 for the semester project, 
  which would allow for approximately 6600 calls to haiku or 2,800 calls to sonnet, 
  depending on how I allocate my usage across development and production phases.



## Notebook 04: Data Collection Pipeline

**Completed:** 2026-04-29 20:33:59

### Section 1 — Web Scraping (TODO 1)

Category: cs.CV
Papers collected: 10

[YOUR REFLECTION HERE]

- Which category did you choose and why?
cs.CV - Computer Vision is a field that has seen significant advancements in recent years, and it is highly relevant to my project topic. 
I chose this category because I am interested in exploring the latest research and developments in computer vision, 
which can provide valuable insights and inspiration for my project.

- How clean was the extracted text? Any issues with formatting?
The extracted text was relatively clean, but there were some issues with formatting.
Some papers had special characters or formatting that did not translate well into plain text, which required additional cleaning. 
Overall, the quality of the extracted text was good, but it may require some manual review to ensure that all relevant information is captured accurately.

- What percentage of papers seem relevant to your project topic?
Based on a quick review of the titles and abstracts, I would estimate that around 70-80% of the papers in the cs.CV category are relevant to my project topic.
This is because computer vision encompasses a wide range of topics, and many papers in this category are likely to be related to my project focus. However, I will need to conduct a more thorough review of the papers to determine their relevance more accurately.

---

### Section 2 — PDF OCR (TODO 2)

[YOUR REFLECTION HERE]

- Which PDFs did you OCR?
 https://arxiv.org/abs/2604.02322
- How accurate was the OCR output? Any errors or garbled text?
 The OCR output was fairly accurate, but there were some issues with formatting . 
 For example, the PDF has two columns, and the layout of the text was mixed the first column and the second column.


- When would you use pdfplumber vs. Tesseract for a given PDF?
    pdfplumber is best for PDFs that have a text layer, which means the text can be directly extracted. 
    This is common for digitally created PDFs. Tesseract is necessary for scanned PDFs or those that are essentially images, where there is no text layer to extract from. In such cases, Tesseract can perform OCR to convert the images of text into actual text data.

- What cleaning steps would the OCR output need before it could be used as training data?
    The OCR output may contain errors such as misrecognized characters, especially for complex layouts or low-quality scans. Cleaning steps could include:
    - Removing line breaks and hyphenation that occur at the end of lines.
    - Correcting common OCR errors (e.g., '0' vs 'O', '1' vs 'l').
    - Reconstructing the original layout if necessary (e.g., separating columns).
    - Removing any non-text elements that were incorrectly recognized as text.

---

### Section 3 — ASR Transcription (TODO 3)

Videos transcribed: 3

- Which videos did you transcribe? Why did you choose them?
"https://www.youtube.com/watch?v=oz5yZc9ULAc",   # Video 1 title: Video PreTraining (VPT): Learning to Act by Watching Unlabeled Online Videos (Paper Explained)
    "https://www.youtube.com/watch?v=or8AcS6y1xg",   # Video 2 title: Optical Character Recognition (OCR)
    "https://www.youtube.com/watch?v=jO-1rztr4O0",   # Video 3 title: How Does Optical Character Recognition (OCR) Work?
They are all related to my project topic, which is about pretraining data collection and processing. 
The first video is about a new method for learning from unlabeled videos, which is relevant to my interest in multimodal data. 
The second and third videos are about OCR, which is a common technique for extracting text from images, and I wanted to see how well the ASR model can handle technical terms related to OCR.

- How accurate was the tiny model on domain-specific vocabulary (technical terms)?
The tiny model did a decent job on general language, but it struggled with some of the technical terms related to OCR.

- What would you get with 'base' or 'small' model size instead?
The 'base' or 'small' models would likely provide better accuracy, especially on domain-specific vocabulary.
 They have more parameters and were trained on more data, which allows them to better capture the nuances of language, including technical terms. However, they would also take significantly longer to run, especially on

- Where does transcribed speech data fit into LLM pretraining? What's unique about it
  When used for LLM pretraining, transcribed speech data can provide a rich source of conversational and informal language, 
  which is often underrepresented in web text. This can help the model learn to understand and generate more natural, human-like language
  What's unique about transcribed speech data is that it often includes features of spoken language that are not present in written text, such as:
- Informal language and slang
- Spoken grammar and sentence fragments
- Filler words (e.g., "um", "uh", "like")
- Disfluencies and repetitions
- Prosodic features (e.g., emphasis, intonation) that may be reflected in punctuation or formatting in the transcript

  compared to web text? (Think: informal language, spoken grammar, filler words)
  Compared to web text, transcribed speech data can provide a more diverse range of language styles and structures,
   which can help the LLM learn to handle a wider variety of inputs and generate more natural responses.
    However, it also introduces noise and variability that can make training more challenging, 
    so careful preprocessing and filtering may be necessary to ensure the quality of the training data.

---

## Notebook 05: Data Cleaning Pipeline Decisions

**Completed:** 2026-04-30 16:41:24

### Pipeline Statistics

| Stage | Documents |
|---|---|
| 0_original | 10 |
| 1_after_html_strip | 10 |
| 2_after_lang_filter | 10 |
| 3_after_dedup | 10 |
| 4_after_pii | 10 |


### TODO 1 — Language Filtering
- What language distribution did you observe in your data?
 The majority of the documents were in English, with a small portion in Japanese and some that were too short to detect a language. 
 The exact distribution would depend on the content of arxiv_clean.json, but based on the synthetic data, we had mostly English texts, 
 a few non-English texts, and some that were removed due to being too short.   

- Did filtering change anything significant for arXiv data? Why or why not?
    Depending on the original language distribution in arxiv_clean.json, filtering could significantly reduce the dataset if there were many non-English documents. 
    If arXiv data is predominantly in English, the impact might be minimal. However, if there were a substantial number of non-English papers,
     filtering would lead to a much smaller dataset, which could affect model performance and generalization. 
- When would you want to keep non-English data?

    I would want to keep non-English data if you are building a multilingual model that aims to support multiple languages.
    Additionally, if the non-English data is relevant to domain and have the resources to process it, it could enhance the model's capabilities. 
    For example, if you are training a model for scientific literature, keeping non-English papers could provide valuable insights and knowledge that would be missed if you only kept English texts.

### TODO 2 — MinHash Deduplication
- What percentage of your corpus was deduplicated?
    The percentage of the corpus that was deduplicated is 20%.

- Did you expect more or fewer duplicates? Why?
        I expected to find some duplicates in the synthetic data since it was intentionally designed to include exact and near-duplicates. 
        However, the MinHash algorithm with a threshold of 0.7 may not have identified the near-duplicates as duplicates, which is why we see 0% deduplication. 
        In a real corpus like arXiv abstracts, I would expect to find more duplicates due to common phrases, similar research topics, and cross-posting of papers.
        The actual percentage would depend on the diversity of the abstracts and how many are closely related or identical.

- How would you adjust the threshold (0.7) to be more strict vs. more lenient?
    To be more strict (remove more duplicates), I would lower the threshold below 0.7, which would consider documents with less similarity as duplicates. 
    For example, setting the threshold to 0.5 would likely identify more near-duplicates as duplicates, increasing the percentage of deduplication. 
    Conversely, to be more lenient (remove fewer duplicates), I would raise the threshold above 0.7, which would require documents to be more similar to be considered duplicates. 
    Setting it to 0.9, for instance, would only remove documents that are very closely matched, resulting in fewer removals.

- arXiv abstracts are often cross-posted — did you find any from the same paper?

    In the synthetic data, we had exact duplicates which would be identified as coming from the same paper. 
    In a real arXiv corpus, I would expect to find some abstracts that are identical or nearly identical due to cross-posting across different categories. 
    If the deduplication process identifies such duplicates, it would indicate that the same paper was posted in multiple categories, which is common on arXiv. 
    The presence of these duplicates can skew the training data if not removed, as it would give more weight to those papers in the model's learning process.

### TODO 3 — PII Scan
[YOUR REFLECTION HERE]

- What types of PII were found (if any) in your corpus?
  I found 16 PERSON_NAME entities, which likely correspond to author names mentioned in the abstracts and 2 LOCATION entities, which could be affiliations or locations mentioned in the abstracts.
- arXiv abstracts rarely have PII — what data sources WOULD have PII?
  I think data sources that would have PII include web forums, social media posts, customer reviews, 
  and medical records. These types of data often contain personal information such as names, 
  contact details, locations, and other sensitive information that can be used to identify individuals.
  (Think: web forums, social media, customer reviews, medical records)
- What are the trade-offs of aggressive PII removal?
    Aggressive PII removal can help protect individuals' privacy and comply with data protection regulations. 
    However, it can also lead to the loss of valuable information that may be relevant for training language models. 
    For example, removing names and affiliations from scientific abstracts could hinder the model's ability to learn about researchers 
    and institutions, which are important for understanding the context of the research. 
    Additionally, overzealous PII removal could strip away important details that contribute to the richness and 
    diversity of the training data, potentially reducing the model's performance and generalization capabilities.
  (e.g., removing 'Einstein at Princeton' removes useful factual information)

### TODO 4 — Pipeline Reflection
[YOUR REFLECTION HERE — answer each question]

1. Language filtering:
   - What threshold did you use? Why?
   I used 0.7 as the threshold for language detection, which is a common choice for balancing precision and recall in language identification.
   - Would you change anything for a multilingual project?
   For a multilingual project, I would consider using a more sophisticated language detection approach that can handle code-switching and mixed-language documents.
   I might also set different thresholds for different languages based on their prevalence in the dataset and the model's intended use cases. Additionally, I would ensure that the language detection model is well-trained on
2. Deduplication threshold (0.7 Jaccard):
   - Does 0.7 seem right for your data? What would 0.9 or 0.5 give you?
      0.7 seems like a reasonable threshold for identifying near-duplicates while allowing for some variation in wording. 
      A threshold of 0.9 would be more strict, likely only removing exact duplicates or very close paraphrases, resulting in fewer removals. 
      A threshold of 0.5 would be more lenient, potentially removing documents that are only somewhat similar, which could lead to a significant reduction in the dataset and the loss of valuable information.

   - Near-duplication in academic papers: citations, related work, rewrites — OK to dedup?

      In academic papers, near-duplication can occur due to common phrases, similar research topics, and cross-posting of papers.
      While it is important to remove exact duplicates to prevent overfitting, near-duplicates that contain valuable information 
      should be carefully considered before removal. 
      If the near-duplicates are essentially the same content with minor rephrasing, it may be beneficial to remove them to reduce redundancy. 
      However     if they contain unique information or perspectives, it may be better to keep them to enrich the training data.  

3. PII removal:
   - Would your production system need more aggressive PII removal? Less?
      For a production system, the level of PII removal would depend on the data source and the intended use of the model. 
      If the model is being trained on data that is likely to contain sensitive information (e.g., social media posts, customer reviews, medical records), then more aggressive PII removal would be necessary to protect privacy and comply with regulations. 
      However, if the data source is less likely to contain PII (e.g., scientific abstracts), then a less aggressive approach may be sufficient, allowing for the retention of useful information while still ensuring privacy.  

   - What entity types are most important to anonymize for your project domain?
      The most important entity types to anonymize would depend on the project domain. 
      For a general language model, anonymizing PERSON_NAME, EMAIL_ADDRESS, and LOCATION would be crucial to protect individual privacy. 
      For a medical domain, anonymizing MEDICAL_RECORD, PATIENT_NAME, and CONTACT_INFO would be essential. 
      For a customer review domain, anonymizing USERNAME, EMAIL_ADDRESS, and LOCATION would be important. 
      The key is to identify which types of PII are most likely to be present in the data and pose a risk to privacy, and ensure that those are effectively anonymized. 

4. Overall pipeline:
   - What percentage of original data survived all cleaning stages?
      The percentage of original data that survived all cleaning stages would depend on the specific thresholds and the nature of the data. 
      For example, if we started with 10,000 documents and after language filtering we kept 8,000, after deduplication we kept 6,000, 
      and after PII removal we kept 5,500, then the final percentage would be (5500 / 10000) * 100 = 55%.       

   - Does that ratio make sense given the data source?
      The ratio of surviving data should make sense given the data source and the cleaning criteria. 
      For arXiv abstracts, which are mostly in English and less likely to contain PII, 
      I would expect a relatively high retention rate after language filtering and PII removal,
       with deduplication potentially removing a moderate percentage due to common phrases and cross-posting. 
      If the retention rate is very low, it may indicate that the thresholds are too strict or 
      that the data source has more noise than expected. Conversely, if the retention rate is very high, 
      it may suggest that the cleaning steps are not effectively filtering out unwanted content.

   - What additional cleaning steps would you add for production use?
      For production use, additional cleaning steps could include:
      - Removing boilerplate text or common phrases that do not add value to the training data.
      - Normalizing text (e.g., lowercasing, removing punctuation) to reduce vocabulary size and improve model learning.
      - Expanding contractions (e.g., "don't" → "do not") to improve consistency in the data.
      - Removing stop words if they are not useful for the model's intended tasks.
      - Handling special tokens or formatting (e.g., LaTeX in scientific papers) to ensure they are appropriately processed.
      - Implementing more advanced deduplication techniques that consider semantic similarity rather than just surface-level similarity.

---

## Notebook 06: Fine-tuning & Alignment Concepts

**Completed:** 2026-05-01 07:55:30

### Training Lifecycle Understanding

The three stages:
1. Pretraining → base model (I built the data pipeline in notebooks 04-05)
2. SFT → instruction-tuned model (requires philanthropy instruction-response pairs)
3. Alignment → DPO or PPO to prefer helpful/harmless outputs

### TODO 1 — SFT Data for My Domain (philanthropy)

- What domain did you choose? Why is it interesting for fine-tuning?
  Philantrophy is an interesting domain for fine-tuning because it involves a wide range of tasks, 
  such as identifying effective charities, optimizing donation strategies, and understanding the impact of philanthropic efforts. 
  A language model assistant specialized in this area could provide valuable insights and recommendations to donors,
   non-profit organizations, and researchers in the field.`

- Looking at the generated pairs: what makes a GOOD training example vs. a bad one?
  A good training example has a clear and specific instruction, a relevant input (if needed), and a correct, helpful output that directly addresses the instruction. 
  It should also be realistic and representative of actual queries that practitioners in the domain might have. 
  A bad training example might have vague instructions, irrelevant inputs, or outputs that are incorrect, unhelpful, or too generic.


- How many high-quality pairs do you think you'd need to noticeably improve a base model?
  The number of high-quality pairs needed to noticeably improve a base model can vary widely depending on the complexity of the task, the quality of the examples, and the size of the base model.
  However, as a rough estimate, fine-tuning with a few hundred to a few thousand high-quality examples can often lead to noticeable improvements in specific tasks or domains. 
  For a significant improvement across a wide range of tasks within a domain, you might need tens of thousands of examples.   

  (Hint: GPT-3's InstructGPT used ~13,000 demonstrations)

### TODO 2 — Fine-tuning Strategy Question

Question asked: Examples:
  - "What LoRA rank should I use for adapting qwen3.5:27b to [domain]?"
  - "How do I create DPO preference pairs when there's no clear 'wrong' answer?"
  - "Can I use LoRA to make the model

- What did you ask and what did you learn?
  "What LoRA rank should I use for adapting qwen3.5:27b to Philanthropy?"
  - "How do I create DPO preference pairs when there's no clear 'wrong' answer?"
  - "Can I use LoRA to make the model respond in a different language?"
  - "What's the minimum GPU I need to fine-tune a 7B model with QLoRA?"
- How does this change your thinking about your project's technical approach?
    The answers to these questions will help me make informed decisions about the fine-tuning and alignment strategies for my project. 
    For example, understanding the appropriate LoRA rank can help me balance performance and resource constraints, while insights on creating DPO preference pairs can guide my approach to alignment when clear 'wrong' answers are not available. 
    Additionally, knowing whether I can use LoRA for language adaptation and the GPU requirements for fine-tuning will influence my technical planning and infrastructure choices.
- Which part of the fine-tuning lifecycle (SFT vs alignment) is most relevant to your project?
    Both SFT and alignment are relevant to my project, but alignment may be particularly crucial given the specialized nature of the domain (philanthropy) and the need to ensure that the model provides accurate and helpful information. 
    While SFT will help the model learn domain-specific knowledge, alignment will be essential to fine-tune the model's behavior and ensure it meets the specific needs and expectations of professionals in the philanthropy field.

### Key Takeaways

- LoRA reduces trainable parameters from billions to millions (0.06% of model size)
- DPO is simpler and more stable than PPO for most use cases
- High-quality SFT data (thousands) beats low-quality SFT data (millions)
- Alignment data: (chosen, rejected) pairs where chosen = preferred behavior

---

## Notebook 07: Test-Time Scaling Experiments

**Completed:** 2026-05-01 16:04:53

### Chain-of-Thought Experiment (TODO 1)

My problem domain: A 3-digit number ABC (digits A,B,C) satisfies:

The digits are all different and A<>0
The number i

- Which style produced the more accurate answer? How do you know?
 They both produced the same answer, which is correct. However, the CoT style provided a detailed reasoning process that clearly showed how it arrived at the answer,
  while the direct style just gave the final answer with simple explanation. Maybe need more complex problem to see the difference.
- Did CoT use more tokens? Was that extra cost worth it?
Sometimes CoT used more tokens, but not always. In this case, the CoT style used more tokens due to the detailed reasoning steps. 
    Whether it's worth it depends on the context; for complex problems where understanding the reasoning is crucial, 
    it can be worth it. For simpler problems, the direct style may suffice.
- For what types of problems does CoT help the most in your domain?
    CoT is especially helpful for problems that require multi-step reasoning, such as data pipeline calculations, cost estimations, scheduling, logic puzzles with constraints, clinical reasoning, and code debugging. 
    In these cases, the step-by-step approach allows for a clearer understanding of the problem-solving process and can lead to more accurate and insightful answers.

---

### Extended Thinking Budget Comparison (TODO 2)

Budget results: [(3000, 12509)]

- How did the answer quality change between budget=500 and budget=3000?
 Since the input problem is quite complex and requires detailed reasoning, there is no output, since the input has already arrived 500 tokens. 
 With a budget of 3000 tokens, the model provided a very high-level answer, however only a brief summary because of the limited token budget.

- Was the quality improvement worth the extra cost? (More output tokens = more cost)
    The quality improvement from 500 to 3000 tokens was significant, as the model was able to provide a much more detailed and comprehensive answer with the larger budget. 
    However, whether it was worth the extra cost depends on the specific use case and requirements. For critical tasks where accuracy and depth of reasoning are essential, the extra cost may be justified. 
    For simpler tasks or when budget constraints are tight, the smaller budget might be sufficient.

- For your production use case, what budget_tokens setting would you choose?
 I would choose a budget_tokens setting of around 2000-4000 for my production use case, as it provides a good balance between answer quality
  and cost.

- When would you use extended thinking vs. standard CoT?
    Extended thinking is particularly beneficial for complex problems that require deep reasoning and multi-step solutions, as it allows the model to generate intermediate thoughts and refine its answer iteratively. 
    Standard CoT may be sufficient for simpler problems or when a quick answer is needed without the need for detailed reasoning. 
    The choice between the two would depend on the complexity of the problem and the importance of having a well-reasoned answer.

---

### Quantization Speedup (TODO 3 — Experiment 3)

- What speedup did you observe for float16 vs float32?
    In the benchmark, we observed a speedup when using float32 compared to float16. 
    It is out of expectation, since float16 is generally expected to be faster than float32 due to reduced memory bandwidth and better GPU utilization.
    Since I used CPU, so there is no benefit from float16, and the overhead of using float16 on CPU may actually make it slower than float32.
    The reason are following:
    1. CPU does not have native support for float16, so it has to emulate float16 operations using float32, which can introduce overhead and reduce performance.
    2. The reduced precision of float16 can lead to increased numerical instability and more frequent overflows/underflows, which can further degrade performance on CPU. 
    3. Many operations internally convert:float16 → float32 → compute → float16


- For qwen3.5:27b (your local model), approximately how much GPU memory does it need
    The qwen3.5:27b model, when loaded in float16 precision, would require approximately 27 billion parameters * 2 bytes/parameter = 54 GB of GPU memory. 
    This is a rough estimate and the actual memory usage may be higher due to additional overhead from the model architecture, activations, and other factors. 
    However, it should fit on a consumer GPU with 24GB of VRAM if we use techniques like model parallelism or offloading parts of the model to CPU memory.

  in float16? Would it fit on a consumer GPU (24GB)?
    The qwen3.5:27b model in float16 would require approximately 54 GB of GPU memory, which exceeds the 24 GB available on a consumer GPU. 
    Therefore, it would not fit on a single consumer GPU without using techniques like model parallelism, offloading, or quantization to reduce memory usage.
- What's the trade-off between int8 quantization vs float16?
    The trade-off between int8 quantization and float16 precision involves a balance between memory efficiency, computational speed, and model accuracy. 
    Int8 quantization reduces the model size by representing weights and activations with 8 bits instead of 16 bits (float16) or 32 bits (float32), which can lead to significant memory savings and faster inference times. 
    However, this reduction in precision can also lead to a loss in model accuracy, especially for models that are sensitive to quantization. 
    Float16 offers a middle ground, providing reduced memory usage compared to float32 while maintaining better accuracy than int8 quantization.

- How does quantization relate to test-time scaling? (Hint: same GPU budget = ?)
    Quantization allows us to fit larger models or use more of the model's capacity within the same GPU memory budget. 
    For example, if a model in float16 requires 54 GB of memory, quantizing it to int8 could reduce that requirement to around 27 GB, allowing it to fit on a 24 GB GPU with some room for activations and overhead. 
    This means that with quantization, we can potentially use a more powerful model or allocate more tokens for reasoning within the same GPU budget, which can enhance test-time scaling and improve performance on complex tasks.

---

## Notebook 08: Project Integration & Week 2 Wrap-up

**Completed:** 2026-05-02 15:16:04

### Project Data Strategy Summary

Domain: Language Learning / Education
Approach: [fine-tuning /  prompt engineering / hybrid]
Rationale: [The include a mix of fine-tuning for domain-specific adaptation and prompt engineering for flexible interaction]

### Architecture Constraints (TODO 3)

- What surprised you about the architecture constraints for your domain?
 What surprised me the most about the architecture constraints for my domain was the realization that even with 
 a relatively small dataset of around 50K tokens, I could still encounter inputs that exceed typical context window limits,
  especially if I consider the possibility of including longer documents or aggregating multiple sources. 
  This highlighted the importance of designing a flexible data strategy that incorporates techniques 
  like chunking and RAG from the outset, rather than assuming that my inputs will always fit within a standard context window.
   It also made me think more critically about how to balance the richness of the input data with the practical limitations of current 
   LLM architectures.

- How will context window limits affect your project design?
Context window limits will significantly influence my project design by necessitating the implementation of strategies to manage longer inputs.
 I will need to incorporate chunking to break down longer documents into manageable pieces, and potentially use RAG to retrieve relevant information from a larger corpus without overwhelming the model. 
 This means that my data pipeline will need to be designed with these constraints in mind, ensuring that I can still provide the model with the necessary context while adhering to its limitations.
 Additionally, I may need to prioritize which information is most critical for the model to process, potentially using summarization or hierarchical approaches to distill the most relevant content.

- What trade-off between model size and latency makes sense for your use case?
For my use case, which involves creating a personalized language learning companion, I believe that a smaller model (around 7B parameters) would be more appropriate given the need for lower latency and the interactive nature of the application.
While larger models (27B+) may offer improved performance on certain tasks, the increased latency and computational requirements could hinder the user experience, especially if the model is being used in a real-time conversational setting. 
By starting with a smaller model, I can ensure that responses are generated quickly, which is crucial for maintaining engagement in a language learning context. 
As I gather more data and better understand the specific requirements of my application, I can consider fine-tuning or even scaling up to a larger model if the benefits outweigh the costs in terms of latency and resource usage.

### Week 2 Impact on My Project

[Summarize how Week 2 changed your thinking about your project:
 - What will you do differently based on understanding transformer architecture?
 - How does the data pipeline apply to your use case?
 - Which Week 2 tool was most useful for your project? Why?]

### Total API Cost for Homework 2

Calls: 2
Input tokens: 350
Output tokens: 1,148
Total cost: $0.0183

---
