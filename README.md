## Natural-Deduction-Proof-Checker
The goal of the project is to develop a programming language that eases writing, automates validating and enables reusing Natural Deduction proofs. The built checker should be published as a Visual Studio Code plug-in/extension for open use.

### Topics Involved       
- Discrete Structures for Computer Science
- Compiler Construction
- Basic Knowledge in Development

----

### Description of the Project
We have automated the process of proof checking with the set of inference rules and axioms that are already defined. Given a set of hypothesis and a target inference, the user can enter the proof in the language we created and the interpreter will check for the correctness of each and every line written. Each line has to be written in a predefined format, for example, say the proposition along with its reason in a specific syntax just like how a normal programming language works like.

----

### Brief Working of the Language
We have designed the context-free grammar for the AST, created the lexer and the parser for the interpreter as well. We had used the SLY package of Python to achieve the same. SLY provides a lexer and parser library by itself. So we were able to directly incorporate it in designing our language. When the user enters a natural deduction proof statement, the lexer first tokenizes the statements, then the parser validates the statements based on the reason provided by the user. These reasons are compared against the logical section of the parser to ensure everything follows from the preceding statements according to the inference rules defined. These inference rules can be customly defined by `admitting` only the necessary rules that are allowed. The theorems that have been proved can also be put to use directly as a customly defined new rule in the subsequent theorem-proofs. A dictionary(history) of all the proofs that have been encountered so far is maintained so that it can be used in the latter part of the derivations. If there is some error in the proof, then the parser will raise an Exception and notify the reason for the error. 

Some common snippets which are part of the language has been incorporated. Find the detailed syntax documentation of the language [here]().

We have used an interpreter for our project since designing a compiler would be too complicated for this project. Besides with an interpreter we could easily decode whatever the user has written line-by-line directly without much effort. The slowness of interpreters won't cause an issue since the proof statements are not generally huge. Therefore an interpreter would per se satisfy the needs of the language.

----

### Phases of the Project

#### 1. Getting equipped
- Understand **First Order Logic (FOL)** and the **Inference Rules** (CS'23 and 24 students must be familiar with this from the Discrete Structures course in 2-1).
- **Compiler Construction** - Understand how programming languages are designed ( You can find the detailed foundation course for this [here](https://drive.google.com/file/d/1EPnYRilh0BotLJGqWqhgtcNTQyMj71Zt/view?usp=share_link) 
):
    - Components of a compiler (on a high-level): Scanner and Parser
    - Context-Free Grammar (CFG)
    - Abstract Syntax Tree (AST)  

- Get familiar with **SLY**, the Python language implementation of the tools used to write scanners and parsers.
  You can find more about SLY in the [Official Documentation](https://sly.readthedocs.io/en/latest/sly.html)

#### 2. Building the language
- The current version of the project is built without the use of Quantifiers:-
    - Designed the **Syntactical structure** of the programming language i.e. the format/syntax for writing the proofs.
    - Built the **Scanner** using SLY.
    - Defined the **Context-free Grammar**, the set of instructions that help in building the AST.
    - Designed the **Validation Logic** used to check if each step of the proof is inferred correctly using the appropriate inference rules and valid referenced expressions.
    - Built the **Parser** based on the CFG and validation-logic using SLY. (Each step will be verified in the parser just as the statement is parsed)
- Incorporated **Custom Inferences** - the rules which can be used anywhere and anytime during the derivations
- Incorporated **Re-use of Inferred Theorems** - the theorems which have been proved already can be directly used in the rest of the proof statements
- Planning to incoporate **Generic Inferences** - create something like a library that stores snippets of proofs of commonly used derivations for added convenience in terms of removed redundancy, increased readability and improved efficiency of writing a proof.

#### 3. VSCode Plug-in
- Publish the proof checker as a VSCode extension.
New to it too :/ But [this](https://www.freecodecamp.org/news/making-vscode-extension/) makes it look straightforward :)

----

#### Mentor
Aryan Gupta (Ph: 7506115192, Email: f20190017@goa.bits-pilani.ac.in / aryan.gupta8501@gmail.com)

#### Faculty Supervisor
[Dr. Anup B Mathew](https://www.bits-pilani.ac.in/goa/anupm/profile)

#### Contributors
- Harshit Samar (2020A7PS0964G)
- Saket B (2020A7PS0983G)
- Atharva Limaye (2020A7PS1721G)

----
