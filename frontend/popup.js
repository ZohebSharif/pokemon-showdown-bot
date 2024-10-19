document.getElementById('get-move').addEventListener('click', function() {
    // Call the content script to get the best move
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        function: suggestMove
      });
    });
  });
  
  // This function will be executed in the context of the Pokémon Showdown page
  function suggestMove() {
    const move = "Thunderbolt"; // Simulate optimal move logic
    document.getElementById('move-suggestion').innerText = "Suggested Move: " + move;
  }