import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getEventByName } from '../services/api';

function EventPage() {
  const { eventName } = useParams();
  const [event, setEvent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEvent = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await getEventByName(eventName);
        setEvent(res.data);
      } catch (err) {
        setError('Falha ao buscar o evento, ou o evento não possui edições cadastradas');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvent();
  }, [eventName]);

  if (isLoading) {
    return <p>Carregando evento...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!event) {
    return <p>Nenhum evento encontrado.</p>;
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', margin: '0 auto', maxWidth: '800px', padding: '20px' }}>
      <h1>{event.nome}</h1>
      <h2>Edições</h2>
      <ul>
        {event.edicoes.map(edicao => (
          <li key={edicao.id}>
            <Link to={`/events/${eventName}/${edicao.ano}`}>{edicao.ano}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default EventPage;