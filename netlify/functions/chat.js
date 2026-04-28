exports.handler = async function(event, context) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { messages } = JSON.parse(event.body);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 200,
        system: `You are a helpful assistant for Top DFW House Buyers, a cash home buying company in Dallas-Fort Worth, Texas. We buy houses for cash anywhere in DFW — Plano, Frisco, Allen, McKinney, Richardson, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake, North Richland Hills, Hurst, Euless, Bedford, Arlington, Garland, Mesquite, Grand Prairie and all DFW cities. Phone: 972-284-9713. No repairs needed, no fees, no commissions. Cash offers within 24 hours, close in 7 days. TX License #0657354. Keep responses SHORT — 2-3 sentences max. Be warm and empathetic. Always guide sellers toward filling out the form or calling 972-284-9713.`,
        messages: messages
      })
    });

    const data = await response.json();

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ reply: data.content[0].text })
    };

  } catch(err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
