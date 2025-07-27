fetch('https://api.xabcstack.com/x-urls/track',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:location.href})}).catch(()=>{});
