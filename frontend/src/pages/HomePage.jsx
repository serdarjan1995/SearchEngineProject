import React from 'react';
import SearchBar from '../components/SearchBar';
import { Button, Typography, Box } from '@mui/material';

function HomePage() {
    return (
        <Box sx={styles.wrapper}>
            <header style={styles.header}>
                <Typography variant="h4" sx={styles.logo}>
                    🔍 QuickFind
                </Typography>
            </header>
            <main style={styles.main}>
                <Typography variant="h5" sx={styles.title}>
                    Your Minimal Search Engine
                </Typography>
                <SearchBar />
            </main>
            <footer style={styles.footer}>
                <Typography variant="body2">
                    Made with 💙 for Searchers
                </Typography>
            </footer>
        </Box>
    );
}

const styles = {
    wrapper: {
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: '"Segoe UI", sans-serif',
        backgroundColor: '#f8f9fa',
        color: '#202124',
    },
    header: {
        padding: '20px',
        textAlign: 'center',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
    },
    logo: {
        margin: 0,
        color: '#1a73e8',
        fontWeight: 600,
    },
    main: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
    },
    title: {
        fontSize: '24px',
        marginBottom: '30px',
        color: '#5f6368',
    },
    footer: {
        padding: '15px',
        textAlign: 'center',
        backgroundColor: '#f1f3f4',
        fontSize: '14px',
        color: '#5f6368',
    },
    learnMoreButton: {
        marginTop: '30px',
        backgroundColor: '#1a73e8',
        fontWeight: 'bold',
        color: 'white',
        ':hover': {
            backgroundColor: '#145ab8',
        },
    },
};

export default HomePage;