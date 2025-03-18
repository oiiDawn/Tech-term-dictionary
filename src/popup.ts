window.addEventListener("load", () => {

  // 1. Check supported or not
  chrome.storage.local.get(null, (data) => {
    if (!data) {
      const message = document.createElement("div");
      message.innerText = "This extension is not supported on this page.";
      message.style.position = "fixed";
      message.style.top = "50%";
      message.style.left = "50%";
      message.style.transform = "translate(-50%, -50%)";
      message.style.padding = "20px";
      message.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
      message.style.color = "white";
      message.style.fontSize = "18px";
      message.style.zIndex = "9999";
      message.style.borderRadius = "5px";
      document.body.appendChild(message);
    }
  });

  // 2. Extract element
  const titleElement = document.getElementById("title")! as HTMLElement;
  chrome.storage.local.get("title", (data) => {
    if (data.title) {
      titleElement.textContent = data.title;
    }
  });
  const descriptionElement = document.getElementById("description")! as HTMLElement;
  chrome.storage.local.get("description", (data) => {
    if (data.description) {
      descriptionElement.textContent = data.description;
    }
  });

  // 3. Highlight
  const button = document.getElementById("highlightButton")! as HTMLElement;
  button.addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      const tabId = tabs[0].id!;
      chrome.tabs.sendMessage(tabId, {action: "highlightElement"}, (response) => {
        console.log(response.message);
      });
    });
  });


});
