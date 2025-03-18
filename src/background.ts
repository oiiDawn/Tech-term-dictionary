chrome.runtime.onInstalled.addListener(() => {
  console.log("✅ Extension Installed: Background Active");
  // 创建右键菜单项
  chrome.contextMenus.create({
    id: "logSelectedText", // 唯一标识符
    title: "Generate Explanation", // 显示在右键菜单中的文字
    contexts: ["selection"] // 仅当用户选择文本时显示菜单项
  });
});
// 监听 Tab 更新（检查是否是 Developer Privacy Policy 页面）
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    console.log("🌍 页面加载完成:", tab.url);
    // 读取存储的隐私政策 Tab ID
    chrome.storage.local.get(["privacyTabId", "savedSkillData"], (data) => {
      if (data.privacyTabId && tabId === data.privacyTabId) {
        console.log("✅ 确定当前 Tab 是用户刚刚点击的隐私政策页面，恢复 Skill 数据");
        // 发送数据到 content.js，让它恢复数据
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs.length > 0) {
            const tabId = tabs[0].id!;
            chrome.tabs.sendMessage(tabId, {action: "restoreData"},
              () => chrome.storage.local.remove("privacyTabId"));
          } else {
            console.log("No active tab found.");
          }
        });
      }
    });
  }
});

chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "privacyPolicyClicked") {
    chrome.tabs.onCreated.addListener((tab) => {
      console.log("🌍 发现新 Tab 创建，可能是隐私政策页面:", tab.id);
      // 存储这个新 Tab ID
      chrome.storage.local.set({privacyTabId: tab.id});
    });
  }
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "logSelectedText") {
    // 获取选中的文本并打印到 console
    console.log("Selected Text: ", info.selectionText);
  }
});