import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function SearchBar({ initialQuery = '', onSearch = null }) {
    const [query, setQuery] = useState(initialQuery);
    const navigate = useNavigate();

    const handleSearch = () => {
        if (query.trim()) {
            const searchUrl = `/search?q=${encodeURIComponent(query)}&p=1`;
            navigate(searchUrl);
            if (location.pathname + location.search === searchUrl && onSearch) {
                onSearch(query);
            }
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', maxWidth: 600, mx: 'auto' }}>
            <TextField
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyPress}
                label="Search"
                variant="outlined"
                fullWidth
                autoFocus
            />
            <Button
                variant="contained"
                onClick={handleSearch}
                sx={{ whiteSpace: 'nowrap', height: '56px' }} // match TextField height
            >
                Search
            </Button>
        </Box>
    );
}

const styles = {
    searchBox: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        maxWidth: '600px',
        margin: '0 auto',
    },
    searchInput: {
        marginBottom: '15px',
    },
    searchButton: {
        padding: '10px 20px',
        fontSize: '16px',
        backgroundColor: '#1a73e8',
        color: 'white',
        '&:hover': {
            backgroundColor: '#145ab8',
        },
    },
};

export default SearchBar;
