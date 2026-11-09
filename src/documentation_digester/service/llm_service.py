from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough


class LlmService:
    def __init__(
        self,
        llm: BaseChatModel,
    ):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(""""""),
                HumanMessagePromptTemplate.from_template("{prompt}"),
            ]
        )
        self.answer_chain = (
            {"prompt": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )

    def ask(self, prompt: str) -> str:
        return self.answer_chain.invoke(prompt)
