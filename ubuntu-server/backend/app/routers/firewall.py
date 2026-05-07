from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from .. import models, database
from ..services import nftables_mgr, abuseipdb

router = APIRouter(prefix="/api/firewall", tags=["firewall"])

class IPRequest(BaseModel):
    ip_address: str
    reason: str = "Manual Action via SOC"

@router.get("/blocked", response_model=List[dict])
def get_blocked_ips(db: Session = Depends(database.get_db)):
    active_blocks = db.query(models.BlockedIP).filter(models.BlockedIP.is_active == True).all()
    # Cross-reference with live nftables state
    system_ips = nftables_mgr.get_blocked_ips()
    
    return [
        {
            "ip": b.ip_address,
            "threat_score": b.threat_score,
            "country": b.country_code,
            "reason": b.reason,
            "in_system": b.ip_address in system_ips,
            "created_at": b.created_at
        } for b in active_blocks
    ]

@router.post("/block")
def block_ip(req: IPRequest, db: Session = Depends(database.get_db)):
    # 1. Check Threat Intel (AbuseIPDB)
    intel = abuseipdb.check_ip(req.ip_address)
    
    # 2. Apply Block in Linux Kernel (nftables)
    success = nftables_mgr.block_ip(req.ip_address)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply nftables rule")
        
    # 3. Save to Database
    db_ip = db.query(models.BlockedIP).filter(models.BlockedIP.ip_address == req.ip_address).first()
    if not db_ip:
        db_ip = models.BlockedIP(
            ip_address=req.ip_address,
            reason=req.reason,
            threat_score=intel.get("threat_score", 0),
            country_code=intel.get("country_code", "Unknown")
        )
        db.add(db_ip)
    else:
        db_ip.is_active = True
        db_ip.threat_score = intel.get("threat_score", 0)
        db_ip.country_code = intel.get("country_code", "Unknown")
        db_ip.reason = req.reason
        
    db.commit()
    return {"status": "success", "ip": req.ip_address, "threat_intel": intel}

@router.post("/unblock")
def unblock_ip(req: IPRequest, db: Session = Depends(database.get_db)):
    # 1. Unblock in Linux Kernel
    success = nftables_mgr.unblock_ip(req.ip_address)
    
    # 2. Update Database
    db_ip = db.query(models.BlockedIP).filter(models.BlockedIP.ip_address == req.ip_address).first()
    if db_ip:
        db_ip.is_active = False
        db.commit()
        
    return {"status": "success" if success else "failed", "ip": req.ip_address}

@router.get("/threat/{ip_address}")
def check_threat(ip_address: str):
    return abuseipdb.check_ip(ip_address)
