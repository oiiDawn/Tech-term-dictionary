const regex = /amazon\.com.+\/dp\/[A-Z0-9]{10}\/ref=.+s=digital-skills/;

window.addEventListener("load", () => {
  console.log("🔍Content script loaded");
  // 提取 Alexa Skill 页面数据
  const isDetailPage = regex.test(window.location.href);
  const skillTitleElement = document.querySelector<HTMLDivElement>('div[data-cy="skill-title"][role="heading"]');
  const skillDescriptionElement = document.querySelector<HTMLDivElement>('div[data-cy="skill-product-description-see-more"]');
  const skillData = {
    title: skillTitleElement ? skillTitleElement.innerText.trim() : "未知技能",
    description: skillDescriptionElement ? skillDescriptionElement.innerText.trim() : "无描述",
    isDetailPage: isDetailPage
  };
  if (isDetailPage) {
    console.log("📊 提取到的数据:", skillData);
    chrome.storage.session.set({ currentSkillData: skillData }, () => console.log("storage.session set done."));
    // 查找 Developer Privacy Policy 超链接
    const policyXpath = "//a[text()='Developer Privacy Policy']";
    const policyXpathResult = document.evaluate(policyXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    const policyLinkElement = policyXpathResult.singleNodeValue as HTMLAnchorElement;
    if (policyLinkElement) {
      console.log("🔗 Developer Privacy Policy 超链接找到:", policyLinkElement.href);
      policyLinkElement.addEventListener("click", () => {
        console.log("📤 用户点击了隐私政策超链接，记录 Skill 数据...");
        // 存储 Skill 数据到 local，保证跨页面可用
        chrome.storage.local.set({ savedSkillData: skillData }, () => console.log("storage.local set done."));
        // 监听新 Tab 创建
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