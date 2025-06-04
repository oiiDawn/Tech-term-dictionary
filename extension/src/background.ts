import axios from "axios";

const llamaAPI = "http://localhost:8000/query";

chrome.runtime.onInstalled.addListener(() => {
  console.log("✅ Extension Installed: Background Active");
  chrome.contextMenus.create({
    id: "logSelectedText", // extension unique id
    title: "Generate Explanation", // text
    contexts: ["selection"] // when show this extension
  });
});
// check if it is policy page
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete") {
    chrome.storage.local.get(["privacyTabId", "savedSkillData"], (data) => {
      if (data.privacyTabId && tabId === data.privacyTabId) {
        console.log("✅ Policy page: restoring data...");
        // to content.ts
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
      chrome.storage.local.set({privacyTabId: tab.id});
    });
  }
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "logSelectedText") {
    const selectionText = info.selectionText!;
    console.log("Selected Text: ", selectionText);
    chrome.storage.local.get(["savedSkillData"], (data) => {
      const title = data.savedSkillData.title;
      const description = data.savedSkillData.description;
      const body = {
        term: selectionText,
        title: title,
        description: description,
        snippet: ""
      }
      console.log(body);
      axios.post(llamaAPI, body, {
        headers: {
          'Content-Type': 'application/json',
        }
      }).then(response => {
        console.log(response);
      })
    });
  }
});