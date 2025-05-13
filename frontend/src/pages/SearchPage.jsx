import React, {useEffect, useState} from 'react';
import {useLocation, useNavigate} from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import Results from '../components/Results';
import Processing from "../components/Processing";

const useQuery = () => new URLSearchParams(useLocation().search);

const backendUrl = import.meta.env.VITE_BACKEND_URL;

function SearchPage() {
    const query = useQuery().get('q') || '';
    const page = parseInt(useQuery().get('p') || '1');
    const [requestState, setRequestState] = useState(0);
    const [status, setStatus] = useState("");
    const [statusMessage, setStatusMessage] = useState("");
    const [results, setResults] = useState([]);
    const [totalResults, setTotalResults] = useState(0);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const resultsPerPage = 10;
    const totalPages = Math.ceil(totalResults / resultsPerPage);

    useEffect(() => {
        if (status === 'processing' || status === 'scraping') {
            const interval = setInterval(() => {
                setRequestState(requestState + 1);
            }, 30000); // 30 seconds

            return () => clearInterval(interval); // Clear on cleanup
        }
    }, [requestState]);

    const fetchResults = (q) => {
        fetch(`${backendUrl}/search?q=${encodeURIComponent(q)}&p=${page}`)
            .then((res) => res.json())
            .then((json) => {
                const data = json.data;
                if (!data) {
                    setStatus(json.status);
                    setStatusMessage(json.message);
                    setLoading(false);
                    return
                }
                setStatus("");
                setStatusMessage("");
                setResults(data.results || []);
                setStats(data.stats);
                setTotalResults(data.total_results || 0);
                setLoading(false);

            })
            .catch(() => setLoading(false));
    }

    useEffect(() => {
        if (!query) return;
        setLoading(true);
        fetchResults(query)
    }, [query, page, requestState]);

    const handlePageClick = (p) => {
        navigate(`/search?q=${encodeURIComponent(query)}&p=${p}`);
    };

    return (
        <div style={styles.container}>
            <SearchBar initialQuery={query} onSearch={fetchResults}/>
            {loading ? (
                <p style={styles.loading}>Searching...</p>
            ) : ((status == 'processing' || status == 'scraping') ? <Processing message={statusMessage}/> : (
                    <>
                        <div style={styles.meta}>
                            <h3>Search Results for: <em>"{query}"</em></h3>
                            <p>Total Results: {totalResults}</p>
                            {stats && (
                                <div style={styles.stats}>
                                    <span>🔢 Total URLs: {stats.total_urls}</span>
                                    <span>🔁 Duplicates: {stats.dupe_urls}</span>
                                    <span>✨ Unique: {stats.unique_urls}</span>
                                    <span>⛔️ Ads: {stats.ad_urls}</span>
                                    <span>📛 Promos: {stats.promo_urls}</span>
                                </div>
                            )}
                        </div>
                        <Results results={results}/>
                        <div style={styles.pagination}>
                            {Array.from({length: totalPages}, (_, i) => i + 1).map((p) => (
                                <button
                                    key={p}
                                    onClick={() => handlePageClick(p)}
                                    style={{
                                        ...styles.pageButton,
                                        backgroundColor: p === page ? '#1a73e8' : '#f1f3f4',
                                        color: p === page ? 'white' : '#202124',
                                        fontWeight: p === page ? 'bold' : 'normal'
                                    }}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                    </>
                )
            )}
        </div>
    );
}

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: '30px 20px',
        fontFamily: '"Segoe UI", sans-serif',
        color: '#202124'
    },
    loading: {
        textAlign: 'center',
        fontSize: '18px'
    },
    meta: {
        marginBottom: '20px'
    },
    stats: {
        display: 'flex',
        gap: '15px',
        fontSize: '14px',
        marginTop: '10px',
        color: '#5f6368'
    },
    pagination: {
        marginTop: '30px',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '10px',
        justifyContent: 'center'
    },
    pageButton: {
        padding: '8px 14px',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '14px'
    }
};

export default SearchPage;