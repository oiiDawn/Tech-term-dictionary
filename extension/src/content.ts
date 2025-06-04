const regex = /amazon\.com.+\/dp\/[A-Z0-9]{10}\/ref=.+s=digital-skills/;

window.addEventListener("load", () => {
  console.log("🔍Content script loaded");
  // extract Alexa Skill information
  const isDetailPage = regex.test(window.location.href);
  const skillTitleElement = document.querySelector<HTMLDivElement>('div[data-cy="skill-title"][role="heading"]');
  const skillDescriptionElement = document.querySelector<HTMLDivElement>('div[data-cy="skill-product-description-see-more"]');
  const skillData = {
    title: skillTitleElement ? skillTitleElement.innerText.trim() : "unknown title",
    description: skillDescriptionElement ? skillDescriptionElement.innerText.trim() : "unknown description",
    isDetailPage: isDetailPage
  };
  if (isDetailPage) {
    chrome.storage.session.set({ currentSkillData: skillData }, () => console.log("storage.session set done."));
    // find link
    const policyXpath = "//a[text()='Developer Privacy Policy']";
    const policyXpathResult = document.evaluate(policyXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    const policyLinkElement = policyXpathResult.singleNodeValue as HTMLAnchorElement;
    if (policyLinkElement) {
      policyLinkElement.addEventListener("click", () => {
        // store info to local
        chrome.storage.local.set({ savedSkillData: skillData }, () => console.log("storage.local set done."));
        // to background.ts
        chrome.runtime.sendMessage({ action: "privacyPolicyClicked" });
      });
    }
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === "restoreData") {
    chrome.storage.local.get(null, data => {
      chrome.storage.session.set({
        title: data.title,
        description: data.description,
      }, () => console.log("storage.session set done."));
    })
    sendResponse();
    return true;
  }
});

const style = document.createElement('style');
style.innerHTML = `
  .highlight-target {
    border: 2px solid red !important;
    background-color: yellow !important;
    padding: 5px !important;
    transition: background-color 0.5s ease;
  }
`;
document.head.appendChild(style);