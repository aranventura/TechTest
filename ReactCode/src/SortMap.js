import React, { useState } from 'react';

function MyComponent() {
  const [data, setData] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    var myHeaders = new Headers();
    myHeaders.append("Authorization", "Basic YWRtaW46YWRtaW4=");

    var requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow'
    };

    try {
      const response = await fetch("http://localhost:8000/api/sortmaps", requestOptions);
      setData(await response.json());
      console.log(data);
    } catch (error) {
      console.log('error', error);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Refresh</button>

      {data && (
        <p>Response: {JSON.stringify(data)}</p>
      )}
    </form>
  );
}

export default MyComponent;
