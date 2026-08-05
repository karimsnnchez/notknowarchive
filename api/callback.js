module.exports = async (req, res) => {
  const { code, error, error_description: errorDescription } = req.query;
  const clientId = process.env.OAUTH_GITHUB_CLIENT_ID;
  const clientSecret = process.env.OAUTH_GITHUB_CLIENT_SECRET;

  const renderMessage = (status, payload) => `
    <!doctype html>
    <html><body>
    <script>
      (function() {
        function receiveMessage(e) {
          window.opener.postMessage(
            'authorization:github:${status}:${JSON.stringify(payload).replace(/'/g, "\\'")}',
            e.origin
          );
          window.removeEventListener('message', receiveMessage, false);
        }
        window.addEventListener('message', receiveMessage, false);
        window.opener.postMessage('authorizing:github', '*');
      })();
    </script>
    </body></html>
  `;

  if (error) {
    res.setHeader('Content-Type', 'text/html');
    res.status(200).send(renderMessage('error', { error: errorDescription || error }));
    return;
  }

  try {
    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ client_id: clientId, client_secret: clientSecret, code }),
    });
    const data = await tokenResponse.json();

    if (data.error) {
      res.setHeader('Content-Type', 'text/html');
      res.status(200).send(renderMessage('error', { error: data.error_description || data.error }));
      return;
    }

    res.setHeader('Content-Type', 'text/html');
    res.status(200).send(renderMessage('success', { token: data.access_token, provider: 'github' }));
  } catch (err) {
    res.setHeader('Content-Type', 'text/html');
    res.status(200).send(renderMessage('error', { error: 'token_exchange_failed' }));
  }
};
