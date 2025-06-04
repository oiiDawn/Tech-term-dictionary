import enum


class TermCategory(enum.Enum): 
  DATA_TYPE = "Data Type",
  ENTITY_NAME = "Entity Name",
  DATA_USAGE = "Data Usage",
  DATA_SHARING = "Data Sharing",
  USER_RIGHTS = "User Rights",
  DATA_STORAGE = "Data Storage",
  LEGAL_AND_COMPLIANCE = "Legal and Compliance"


PROMPT = {
  "Data Type":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on what types of data are collected by the skill. '{description}. In their privacy policy, they declare that they collect and process various types of data, including '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know the kinds of personal, sensitive, and usage data involved. Provide examples to illustrate how these data types are relevant when interacting with the Alexa skill.",
  "Entity Name":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on who is responsible for handling users' data. '{description}. In their privacy policy, they declare that '{snippet}' is responsible for managing user data. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should understand the roles of the Data Controller, Data Processor, and any Third Parties involved. Provide examples relevant to how these entities interact within the Alexa ecosystem.",
  "Data Usage":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on how user data is utilized. '{description}. In their privacy policy, they declare that your data will be used for '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know the purposes for which their data is processed and the legal justifications for these uses. Provide examples that demonstrate how this applies to the Alexa skill's functions.",
  "Data Sharing":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on how and why data is shared. '{description}. In their privacy policy, they declare that your data may be shared with '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know which third parties might receive their data and for what purpose. Provide examples of how data sharing occurs within the context of the Alexa skill.",
  "User Rights":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on the rights users have concerning their data. '{description}. In their privacy policy, they declare that users have rights such as '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know about their rights to access, correct, delete, or restrict the use of their data. Provide examples of how these rights can be exercised within the Alexa skill.",
  "Data Storage":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on how user data is stored. '{description}. In their privacy policy, they declare that your data will be stored '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know where their data is kept, for how long, and what security measures are in place. Provide examples relevant to data storage practices within the Alexa ecosystem.",
  "Legal and Compliance":
    "Please write a brief explanation of '{term}' for the understanding of '{title}' Alexa skill privacy policy, focusing on how the skill complies with legal standards and data protection regulations. '{description}. In their privacy policy, they declare that they comply with '{snippet}'. This is the policy snippet with '{term}' in '{title}' privacy policies. Users should know about the safeguards in place to protect their data under laws like GDPR. Provide examples that highlight the skill's compliance measures."
}

