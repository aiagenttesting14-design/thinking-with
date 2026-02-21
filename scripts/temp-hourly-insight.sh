#!/bin/bash
# Temporary hourly insight script until cron is fixed
echo "Running phase-aware insight at $(date)"
python3 scripts/phase-aware-micro-insight-final.py
