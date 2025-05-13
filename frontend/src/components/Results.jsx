import React from 'react';
import { Card, CardActionArea, CardContent, Typography, Box, Button, Grid, Link, Tooltip, IconButton, Paper } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined';
import LanguageOutlinedIcon from '@mui/icons-material/LanguageOutlined';

function Results({ results, stats }) {
  return (
      <Box sx={styles.container}>
        {/* Display stats */}
        {stats && (
            <Box sx={styles.statsContainer}>
              <Typography variant="h6" sx={styles.statsTitle}>Search Statistics</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" sx={styles.statsText}>🔢 Total URLs: {stats.total_urls}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" sx={styles.statsText}>✨ Unique URLs: {stats.unique_urls}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" sx={styles.statsText}>🔁 Duplicate URLs: {stats.dupe_urls}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" sx={styles.statsText}>⛔ Ad URLs: {stats.ad_urls}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" sx={styles.statsText}>📛 Promo URLs: {stats.promo_urls}</Typography>
                </Grid>
              </Grid>
            </Box>
        )}

        {/* Display search results */}
        {results.length === 0 ? (
            <Typography variant="h6" sx={styles.noResults}>No results found. Try a different search.</Typography>
        ) : (
            results.map((result) => (
                <Card key={result.id} sx={styles.resultCard}>

                    <CardContent>
                      <CardActionArea component="a" href={result.url} target="_blank">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6" sx={styles.title}>
                          {result.title}
                        </Typography>
                        <Tooltip
                            title={
                              <Box>
                                <Typography variant="body2"><strong>URL Hash:</strong> {result.url_hash}</Typography>
                                <Typography variant="body2"><strong>Term Frequency:</strong></Typography>
                                <ul style={{ margin: 0, paddingLeft: '1em' }}>
                                  {Object.entries(result.search_term_freq).map(([term, freq]) => (
                                      <li key={term}>
                                        <Typography variant="caption">{term}: {freq}</Typography>
                                      </li>
                                  ))}
                                </ul>
                              </Box>
                            }
                            placement="top"
                            arrow
                        >
                          <IconButton size="small">
                            <InfoOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      </CardActionArea>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {result.info_type === 'html' ? (
                            <LanguageOutlinedIcon fontSize="small" color="disabled" />
                        ) : (
                            <InsertDriveFileOutlinedIcon fontSize="small" color="disabled" />
                        )}
                        <Typography variant="subtitle1" sx={styles.url}>
                          <a href={result.url} target="_blank">{result.url}</a>
                        </Typography>
                      </Box>

                      <Typography variant="body2" sx={styles.url}>
                        {result.desc}
                      </Typography>
                    </CardContent>
                </Card>
            ))
        )}
      </Box>
  );
}

const styles = {
  container: {
    marginTop: '30px',
  },
  statsContainer: {
    marginBottom: '20px',
    backgroundColor: '#f1f3f4',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  },
  statsTitle: {
    fontWeight: 600,
    marginBottom: '10px',
  },
  statsText: {
    color: '#5f6368',
  },
  resultCard: {
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
    transition: 'transform 0.3s',
    '&:hover': {
      transform: 'scale(1.05)',
    },
  },
  title: {
    fontWeight: 600,
    color: '#1a73e8',
  },
  url: {
    marginTop: '8px',
    color: '#5f6368',
  },
  searchTermFreq: {
    marginTop: '10px',
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  term: {
    color: '#202124',
  },
  noResults: {
    textAlign: 'center',
    color: '#5f6368',
    fontSize: '18px',
  },
};

export default Results;
